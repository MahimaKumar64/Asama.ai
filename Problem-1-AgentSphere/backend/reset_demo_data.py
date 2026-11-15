
from app.database.session import SessionLocal
from app.models import Comment, RoutingLog, Post

db = SessionLocal()

try:
    # Delete dependent records first
    comments_deleted = db.query(Comment).delete(
        synchronize_session=False
    )

    routing_logs_deleted = db.query(RoutingLog).delete(
        synchronize_session=False
    )

    posts_deleted = db.query(Post).delete(
        synchronize_session=False
    )

    db.commit()

    print("Demo data reset successfully!")
    print(f"Comments deleted: {comments_deleted}")
    print(f"Routing logs deleted: {routing_logs_deleted}")
    print(f"Posts deleted: {posts_deleted}")
    print("Registered agents have been preserved.")

except Exception:
    db.rollback()
    raise

finally:
    db.close()
