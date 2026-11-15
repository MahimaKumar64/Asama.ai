
from urllib.parse import urlparse

from sqlalchemy import any_, func, literal, not_

from app.models import Agent


def retrieve_candidates(db, post, author, top_k=50):
    """
    Stage 1: Filter ineligible agents.
    Stage 2: Retrieve top candidates using HNSW and lexical search.
    Stage 3: Calculate exact hybrid scores for every eligible agent.

    Returns:
        all_candidates: Every eligible agent with relevance scores.
        top_candidates: Retrieved candidates sent to the LLM reranker.
    """

    author_domain = urlparse(author.webhook_url).hostname or ""

    # --------------------------------------------------
    # Stage 1: SQL metadata filtering
    # --------------------------------------------------

    filters = [
        Agent.is_active.is_(True),
        Agent.id != author.id,
        Agent.interest_embedding.isnot(None),

        not_(
            literal(author.industry_category)
            == any_(Agent.blocked_industries)
        )
    ]

    if author_domain:
        filters.append(
            not_(
                literal(author_domain)
                == any_(Agent.blocked_domains)
            )
        )

    # --------------------------------------------------
    # Stage 2: HNSW dense retrieval
    # --------------------------------------------------

    distance = Agent.interest_embedding.cosine_distance(
        post.post_embedding
    )

    dense_results = (
        db.query(Agent.id)
        .filter(*filters)
        .order_by(distance)
        .limit(top_k)
        .all()
    )

    dense_ids = {
        agent_id
        for agent_id, in dense_results
    }

    # --------------------------------------------------
    # Stage 2B: Lexical retrieval
    # --------------------------------------------------

    search_text = f"{post.title} {post.content}"

    document_vector = func.to_tsvector(
        "english",
        Agent.interest_manifesto
    )

    search_query = func.plainto_tsquery(
        "english",
        search_text
    )

    lexical_rank = func.ts_rank_cd(
        document_vector,
        search_query
    )

    lexical_results = (
        db.query(Agent.id)
        .filter(
            *filters,
            document_vector.op("@@")(search_query)
        )
        .order_by(lexical_rank.desc())
        .limit(top_k)
        .all()
    )

    lexical_ids = {
        agent_id
        for agent_id, in lexical_results
    }

    # Union of dense and lexical retrieval candidates.
    retrieved_ids = dense_ids | lexical_ids

    # --------------------------------------------------
    # Stage 3: Exact scoring for all eligible agents
    # --------------------------------------------------

    all_results = (
        db.query(
            Agent,
            distance.label("distance"),
            lexical_rank.label("rank")
        )
        .filter(*filters)
        .all()
    )

    all_candidates = []

    for agent, distance_value, rank_value in all_results:

        vector_score = max(
            0.0,
            min(1.0, 1.0 - float(distance_value))
        )

        rank_value = float(rank_value or 0.0)

        lexical_score = (
            rank_value / (1.0 + rank_value)
        )

        hybrid_score = (
            0.7 * vector_score
            + 0.3 * lexical_score
        )

        all_candidates.append({
            "agent": agent,
            "vector_score": vector_score,
            "lexical_score": lexical_score,
            "hybrid_score": hybrid_score
        })

    # Sort every eligible agent by hybrid relevance.
    all_candidates.sort(
        key=lambda item: item["hybrid_score"],
        reverse=True
    )

    # --------------------------------------------------
    # Stage 4: Select top retrieved candidates for reranking
    # --------------------------------------------------

    top_candidates = [
        item
        for item in all_candidates
        if item["agent"].id in retrieved_ids
    ][:top_k]

    return {
        "all_candidates": all_candidates,
        "top_candidates": top_candidates
    }
