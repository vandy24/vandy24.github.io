Peter Van Dyke
CSCI 4131
Final Project Readme

1. Project Type: A level
2. Group Members Names: Peter Van Dyke (done solo)
3. https://word-list-vandy123.herokuapp.com/
4. https://github.com/vandy24/vandy24.github.io
5. Bing Maps API, Flask, Heroku, Postgres, SQLAlchemy, bootstrap, wtforms
6. This online web application allows users to post and view reviews of the dorms on the University of Minnesota Campus. To use the site, users need to make an account. Any review a user posts is permanently tied to their account. Reviews consist of a title, review, and up to three optional photos. All reviews are accompanied by a map displaying the location of the dorm in question. This website is particularly helpful for prospective students. Only users who have an account are able to post/view reviews.

When a user navigates to the website, if they aren't logged in they are redirected to the login/register page. Once they've logged in, they are brought to the search page. From here users can input a search query to look for a specific review. Alternatively, users can also click on "New Post" and they are brought to the review creation page. Here they select the dorm they want to review from a dropdown menu, give the review a title, input the review content, and attach links to any related photos (if they wish).

Posts, buildings, images, and users are all stored in different tables of the same database.

7.
* def login():
If the user is logged in, this controller redirects them to the search page. If the user wasn't previously logged in, but fills out the login or register form correctly, it redirects them to the search page. If they just registered it also adds them into the database.

* def search():
This controller checks to make sure the user is logged in. If they are not it redirects them back to the login page. If they are it renders the 'search.html' template.

* def postings_list():
This controller takes the data from the search form, searches the database for matching posts, and renders 'postings_list.html' (the results page). The search results are passed in as a specially formatted list.

* def new_posting():
This controller renders the "new_post.html" template, reads the form data on the page, and creates new image/post records in the database.

8.
* login.html:
This is the template used for the login page. It holds two forms (one for logging in and one for registering).

* new_post.html:
This is the template for creating a new review. It uses the NewPost FlaskForm

* postings_list.html:
This is the template for the search results page. It takes a specially formatted search result list.

* search.html:
This is the template for the search page. It uses the SearchForm FlaskForm.

9.
* users:
This table has a primary key called "email" and one called field "pass_word". Technically, "email" holds a user's username. This table is used for session management. Users have a one to many relationship with posts.

* posts:
This table has the columns "email" (the username of the poster), "title" (the name of the review), "description" (the actual review content), "building" (the name of the building being reviewed), and "id" (a unique id assigned to each post). Posts have one to many relationship with images

* images:
This table has the columns "url" (the link to the image), and "upload_id" (the id of the associated post). This database holds the links to any images uploaded with reviews.

* buildings:
This table has the columns "lat" and "long" (which correspond to the coordinates of the building), "name" (which is the text name of the building), and the primary key "building" (which is a unique integer id assigned to each dorm). Buildings have a 1 to many relationship with posts.

10.
Beyond the technologies listed in #5, this web app also uses "formhelpers.html" which was provided on the class github.
