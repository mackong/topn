import fileinput
import os
import sys
import tempfile
import timeit
from collections import Counter
from typing import Dict, List, Tuple


def split(input_file: str, split_filenames: List[str]) -> None:
    """Split input file into `small` files based on modular of hash value."""
    nsplit = len(split_filenames)
    split_files = [open(fname, 'w') for fname in split_filenames]

    with open(input_file) as f:
        for line in f:
            findex = hash(line) % nsplit
            split_files[findex].write(line)

    [f.close() for f in split_files]


def count_urls(input_file: str, count_file: str, n: int = 100) -> List[Tuple[str, int]]:
    """Count the occurrences of urls in input_file, write the count result into count_file.

    Returns the topn occurrences of urls in descending order.
    """
    c = Counter()
    with open(input_file) as ifp, open(count_file, 'w') as ofp:
        for line in ifp:
            c[line] += 1
        for url, count in c.items():
            ofp.write('{},{}\n'.format(count, url.strip()))
        return c.most_common(n)


def topn(input_file: str, n: int = 100) -> None:
    """Print the topn occurrences of urls in input file."""
    split_prefix = 'split'
    count_prefix = 'count'

    # A prime number may make the distribution more uniform.
    # NOTE: if greater than 1024, we may need to change the limitation of open files.
    nsplit = 1009

    with tempfile.TemporaryDirectory(prefix='topn') as work_dir:
        split_filenames = [os.path.join(work_dir, '{}.{}'.format(split_prefix, i+1)) for i in range(nsplit)]
        count_filenames = [os.path.join(work_dir, '{}.{}'.format(count_prefix, i+1)) for i in range(nsplit)]

        split(input_file, split_filenames)

        url_counter = Counter()
        for split_fname, count_fname in zip(split_filenames, count_filenames):
            url_counter.update(dict(count_urls(split_fname, count_fname, n)))

        least_count = 0
        for url, count in url_counter.most_common(n):
            print(count, url.strip())
            least_count = count

        for url, count in url_counter.most_common()[n:]:
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
