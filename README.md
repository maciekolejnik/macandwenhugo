# Building locally

Run `hugo server` to start a server at localhost:1313. 
Local changes cause an automatic refresh - nice feature.

# Deployment

Use the deployment script `deploy.sh`.
Because the blog is hosted on Github Pages, deploying means
pushing to appropriate repo hosted on Github. To facilitate
that, the `public` directory (which is where the site gets
rendered upon executing `hugo` command) is a git submodule
pointing to the appropriate Github repo (maciekolejnik.github.io).
So the deploy script simply builds the site to `public`
and then pushes the changes to update the repo.

It is important to **not delete** the `public` directory
as that deletes the submodule, which then needs to be added
again for the deploy script to work.

To deploy, simply execute 

```
./deploy.sh <commit_msg>
```

where `<commit_msg>` is an optional commit message.


# processMarkdownExport.py

We write our posts in Notion. Notion has an 'export to markdown'
feature, but the resulting `.md` file has issues. The major ones
are to do with `iframe`s and images, where the URL gets duplicated
for some reason. Also, we drag and drop images into Notion posts
which results in weird image URIs in the exported `.md`. 
Fortunately, the original filenames (of the images) get preserved
which means we can extract them and replace the rest of the URI
with a URL of AWS S3 bucket where we store those images.

Overall, for the file to do its job, the following workflow is 
expected:

1. Write a blog post in Notion, dragging and dropping images from
a local directory (make sure the images are not too heavy, <1MB 
recommended). Don't worry about hugo front matter (--- ... --- stuff).

2. When finished, export the post to markdown. Save the zip file to 
Downloads folder. 

3. Extract the zip into the same folder (Downloads).

4. Now choose a short name that describes the post. Use '-' as a
delimeter. Things like 'wistow-crags-scramble', 'el-realet-ridge',
'lake-district-backpacking' work well. This name will serve as 
- a name for a directory in S3 bucket storing images for this post
- a name for the md file in `contents/post` in hugo
Now you need to rename the extracted folder (inside Downloads)
**and** the folder containing images inside the extracted folder to 
the chosen name. This is important to get right.

5. You can now upload the images to S3, but before you do that, 
you must add a cover image and a small image for the post. Name 
them `cover.jpg` and `small.jpg` and put them in the folder where
all other images are. Then upload to S3. 

6. Now rename the `.md` file (which conatins the blog post) in the 
extracted folder to `post.md`.

7. You can now run 
```
python processMarkdownExport.py <folderName> <date>
```
where `<folderName>` is the name you've chosen in step 4
and `<date>` is the date on which the activity you're writing
about took place.

That should be it. You should now have a new post in `conents/post`;
do check that it's what you expect and report any bugs + any translations
that need to be added.
