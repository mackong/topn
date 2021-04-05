import mmap
import os
import sys
import tempfile
import timeit
from collections import Counter
from typing import Dict, List, Tuple


def split(input_file: str, split_filenames: List[str]) -> None:
    """Split input file into `small` files based on modular of hash value."""
    nsplit = len(split_filenames)
    split_files = [open(fname, 'wb') for fname in split_filenames]

    with open(input_file) as f:
        with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ) as mm:
            for line in iter(mm.readline, b''):
                findex = hash(line) % nsplit
                split_files[findex].write(line)

    [f.close() for f in split_files]


def count_urls(input_file: str, n: int = 100) -> List[Tuple[str, int]]:
    """Count the occurrences of urls in input_file.

    Returns the topn occurrences of urls in descending order.
    """
    c = Counter()
    with open(input_file) as f:
        for line in f:
            c[line] += 1
        return c.most_common(n)


def topn(input_file: str, n: int = 100) -> None:
    """Print the topn occurrences of urls in input file."""
    split_prefix = 'split'

    # A prime number may make the distribution more uniform.
    # NOTE: if greater than 1024, we may need to change the limitation of open files.
    nsplit = 1009

    with tempfile.TemporaryDirectory(prefix='topn') as work_dir:
        split_filenames = [os.path.join(work_dir, '{}.{}'.format(split_prefix, i+1)) for i in range(nsplit)]

        split(input_file, split_filenames)

        url_counter = Counter()
        for split_fname in split_filenames:
            url_counter.update(dict(count_urls(split_fname, n)))

        top10n = url_counter.most_common(n * 10)
        least_count = 0
        for url, count in top10n[:n]:
            print(count, url.strip())
            least_count = count

        for url, count in top10n[n:]:
            if count != least_count:
                break
            print(count, url.strip())
        else:
            # There are more than (nsplit-1)*n duplicate occurrences.
            # Now just a WARNING.
            # TODO: We may need to recalculate from count files.
            print('WARNING: there are too many duplicate occurrences')


if __name__ == '__main__':
    start = timeit.default_timer()

    input_file = sys.argv[1] if len(sys.argv) == 2 else 'urls.base.txt'
    print('Calculate topn for {}'.format(input_file))
    topn(input_file)

    print('\ntime ellapsed: {} seconds.'.format(timeit.default_timer() - start))
