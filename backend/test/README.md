# Testing

To be able to run these tests you need to manually create a new database called ```test_images```.

```
mysql -u root -p
```

```
CREATE DATABASE test_images
```

Tables get dropped and newly created with setup_tables.py before every test run anyways so no need to create them here.

For testing the moving image function also need to create that procedure (see init.sql).