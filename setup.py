import setuptools
import pathlib


try:
    import docutils.core
    from docutils.writers import manpage
except ImportError:
    docutils = None
    manpage = None


from cursedspace import version


with open('README.md', encoding='utf-8') as fd:
    long_description = fd.read()


with open('LICENSE', encoding='utf-8') as fd:
    licensetext = fd.read()


def compile_documentation():
    htmlfiles = []

    if docutils is None:
        return htmlfiles

    dst = pathlib.Path('./cursedspace/docs')
    dst.mkdir(exist_ok=True)
    
    pathlib.Path('./man').mkdir(exist_ok=True)

    man_pter = None

    if None not in [docutils, manpage]:
        for fn in pathlib.Path('./doc').iterdir():
            if fn.suffix == '.rst':
                if fn.stem == 'cursedspace':
                    man_pter = str(fn)
                dstfn = str(dst / (fn.stem + '.html'))
                docutils.core.publish_file(source_path=str(fn),
                                           destination_path=dstfn,
                                           writer_name='html')
                htmlfiles.append('docs/' + fn.stem + '.html')

    if man_pter is not None:
        docutils.core.publish_file(source_path=man_pter,
                                   destination_path='man/cursedspace.3',
                                   writer_name='manpage')

    return htmlfiles


setuptools.setup(
    name='cursedspace',
    version=version.__version__,
    description="Library for TUI programs on basis of curses",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license_file="LICENSE",
    license_files="LICENSE",
    url="https://github.com/vonshednob/cursedspace",
    author="R",
    author_email="devel+cursedspace@kakaomilchkuh.de",
    entry_points={'console_scripts': []},
    packages=['cursedspace'],
    package_data={'cursedspace': compile_documentation()},
    data_files=[('share/man/man3', ['man/cursedspace.3']),
                ('share/applications', []),
                ('share/doc/cursedspace', [])],
    install_requires=[],
    extras_require={},
    python_requires='>=3.0',
    classifiers=['Development Status :: 3 - Alpha',
                 'Environment :: Console :: Curses',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python :: 3',])

