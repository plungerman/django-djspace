django-djspace
==============

Wisconsin Space Grant Consortium grant programs application infrastructure.

# New Data Model

1. create data model class in application/models.py

2. update the applications GM2MField in the UserProfile() data model class with the name of the new class e.g. 'application.NewDataModel',

3. create the form class in application/forms.py

4. execute 'python manage.py migrate --run-syncdb' to create the new table(s)

5. update templates/dashboard/applications.inc.html to add the URL to the application form

6. create admin class in application/admin.py

7. email template for after submission and print view on admin dashboard

8. update application/views.py if need be

9. update templates/application/form.html if need be
