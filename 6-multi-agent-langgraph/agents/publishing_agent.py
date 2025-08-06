import os
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
import re
import markdown

def publishing_agent(state):
    """
    Publishes the final_blog_post to the WordPress website.
    """
    print(" > PUBLISING AGENT")
    final_blog_post = state["final_blog_post"]

    cleaned_post = final_blog_post.strip()
    cleaned_post = re.sub(r"^```(html|markdown)?\s*", "", cleaned_post, flags=re.IGNORECASE)
    cleaned_post = re.sub(r"\s*```$", "", cleaned_post)
    cleaned_post = cleaned_post.strip()

    lines = cleaned_post.split("\n")
    post_title = "Automated Blog Post"
    post_content = cleaned_post

    for i, line in enumerate(lines):
        stripped_line = line.strip()
        if stripped_line.startswith("# "):
            post_title = stripped_line.lstrip("# ")
            post_content = "\n".join(lines[i+1:]).strip()
            break
        else:
            for i, line in enumerate(lines):
                if line.strip():
                    post_title = line.strip()
                    post_content = "\n".join(lines[i+1:]).strip()
                    break

    html_content = markdown.markdown(post_content)

    wp_url = os.getenv("WORDPRESS_URL")
    wp_username = os.getenv("WORDPRESS_USERNAME")
    wp_password = os.getenv("WORDPRESS_PASSWORD")

    if not all([wp_url, wp_username, wp_password]):
        print(" > Wordpress Credentials not found in the .env file")
        return {"published": False}
    
    client = Client(wp_url, wp_username, wp_password)

    post = WordPressPost()
    post.title = post_title
    post.content = html_content
    post.post_status = "publish"

    try:
        client.call(NewPost(post))
        print(f" > Successfully published thew blog post: {post_title}")
        return {"published": True}
    except Exception as e:
        print(f" > Error publishing to the wordpress site of here and now ai: {e}")
        return {"published": False}
