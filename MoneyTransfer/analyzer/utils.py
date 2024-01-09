def handle_uploaded_file(source, dest):
    with open(dest, "wb+") as fp:
        for chunk in source.chunks():
            fp.write(chunk)
