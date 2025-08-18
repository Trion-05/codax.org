import os
import json
from datetime import datetime
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.exception import AppwriteException

def main(context):
    # Initialize Appwrite client
    client = (
        Client()
        .set_endpoint(os.environ["APPWRITE_FUNCTION_API_ENDPOINT"])
        .set_project(os.environ["APPWRITE_FUNCTION_PROJECT_ID"])
        .set_key(context.req.headers["x-appwrite-key"])
    )

    # Connect to Appwrite database
    databases = Databases(client)
    database_id = os.environ["APPWRITE_DATABASE_ID"]
    collection_id = os.environ["APPWRITE_COLLECTION_ID"]

    method = context.req.method
    path = context.req.path

    try:
        # POST: Create a blog post
        if method == "POST" and path == "/blog":
            body = context.req.body_raw
            data = json.loads(body)

            # Required field
            title = data.get("title")
            if not title:
                return context.res.json({"error": "Missing required field: title"}, status=400)

            # Optional fields with defaults
            writer = data.get("writer", "Anonymous")
            date = data.get("date", datetime.utcnow().isoformat())
            photo = data.get("photo", "")
            headline = data.get("headline", "")

            # Create blog document
            doc = databases.create_document(
                database_id=database_id,
                collection_id=collection_id,
                document_id="unique()",
                data={
                    "title": title,
                    "writer": writer,
                    "date": date,
                    "photo": photo,
                    "headline": headline
                }
            )

            return context.res.json({
                "message": "Blog post created",
                "document": doc
            })

        # DELETE: Remove blog post by ID
        elif method == "DELETE" and path.startswith("/blog/"):
            doc_id = path.split("/")[-1]
            if not doc_id:
                return context.res.json({"error": "Missing blog ID"}, status=400)

            databases.delete_document(
                database_id=database_id,
                collection_id=collection_id,
                document_id=doc_id
            )
            return context.res.json({"message": f"Blog post {doc_id} deleted"})

        # Health check route
        elif path == "/ping":
            return context.res.text("Pong")

        else:
            return context.res.json({"error": "Route not found"}, status=404)

    except AppwriteException as err:
        context.error("Appwrite error: " + repr(err))
        return context.res.json({
            "error": "Something went wrong",
            "details": str(err)
        }, status=500)
