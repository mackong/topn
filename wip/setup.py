from distutils.core import setup, Extension

def main():
    setup(name="time33",
          version="1.0.0",
          description="Python interface for the time33 C library function",
          author="mackong",
          author_email="mackonghp@gmail.com",
          ext_modules=[Extension("time33", ["time33module.c"])])

if __name__ == "__main__":
    main()
