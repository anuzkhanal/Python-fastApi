from fastapi import FastAPI, status, HTTPException, Response, Depends, APIRouter
from sqlalchemy import func
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from typing import List, Optional

router = APIRouter(prefix="/posts", tags=["Posts"])


# def find_post(id):
#     for p in my_posts:
#         if p["id"] == id:
#             return p


# def find_index_post(id):
#     for i, p in enumerate(my_posts):
#         if p["id"] == id:
#             return i


@router.get("/", response_model=List[schemas.PostOut])
async def get_posts(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
):
    # cursor.execute(""" SELECT * FROM posts """)
    # posts = cursor.fetchall()

    # to get post of the logged in user only
    # posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all()

    # posts = (
    #     db.query(models.Post)
    #     .filter(models.Post.title.contains(search))
    #     .limit(limit)
    #     .offset(skip)
    #     .all()
    # )

    posts = (
        db.query(models.Post, func.count(models.Vote.post_id).label("Votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.title.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )

    return posts


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse
)
async def create_posts(
    payload: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    # cursor.execute(
    #     """ INSERT INTO posts(posts_title,posts_content,posts_published) VALUES(%s,%s,%s) RETURNING * """,
    #     (payload.title, payload.content, payload.published),
    # )
    # new_post = cursor.fetchone()
    # conn.commit()

    new_post = models.Post(owner_id=current_user.id, **payload.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/{id}", response_model=schemas.PostOut)
async def get_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    # cursor.execute(""" SELECT * FROM posts WHERE posts_id =  %s """, str((id)))
    # post = cursor.fetchone()

    post = (
        db.query(models.Post, func.count(models.Vote.post_id).label("Votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.id == id)
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} not found",
        )

    # to get post of logged in user only
    # if post.owner_id != current_user.id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Not Authorized To Perfom Requested Action",
    #     )

    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    # cursor.execute(""" DELETE FROM posts WHERE posts_id = %s RETURNING *""", str((id)))
    # post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id:{id} was not found",
        )
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Authorized To Perfom Requested Action",
        )

    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.PostResponse)
async def update_post(
    id: int,
    post: schemas.PostUpdate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    # cursor.execute(
    #     """ UPDATE posts SET posts_title = %s, posts_content = %s, posts_published = %s WHERE posts_id = %s RETURNING * """,
    #     (post.title, post.content, post.published, str((id))),
    # )
    # new_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id:{id} was not found",
        )
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Authorized To Perfom Requested Action",
        )

    post_query.update(post.dict(), synchronize_session=False)

    db.commit()

    return post_query.first()
