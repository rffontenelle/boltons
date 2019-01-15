# -*- coding: utf-8 -*-

import platform

from pytest import raises

from boltons.setutils import IndexedSet, _MISSING, complement


_IS_26 = platform.python_version().startswith('2.6')


def test_indexed_set_basic():
    zero2nine = IndexedSet(range(10))
    five2nine = zero2nine & IndexedSet(range(5, 15))
    x = IndexedSet(five2nine)
    x |= set([10])

    assert list(zero2nine) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert set(zero2nine) == set([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    assert list(five2nine) == [5, 6, 7, 8, 9]
    assert x == IndexedSet([5, 6, 7, 8, 9, 10])
    assert x[-1] == 10

    assert zero2nine ^ five2nine == IndexedSet([0, 1, 2, 3, 4])

    assert x[:3] == IndexedSet([5, 6, 7])
    assert x[2:4:-1] == IndexedSet([8, 7])


def test_indexed_set_mutate():
    thou = IndexedSet(range(1000))
    assert (thou.pop(), thou.pop()) == (999, 998)
    assert (thou.pop(499), thou.pop(499)) == (499, 500)

    ref = [495, 496, 497, 498, 501, 502, 503, 504, 505, 506]
    assert [thou[i] for i in range(495, 505)] == ref

    assert len(thou) == 996
    while len(thou) > 600:
        dead_idx_len = len(thou.dead_indices)
        dead_idx_count = thou._dead_index_count
        thou.pop(0)
        new_dead_idx_len = len(thou.dead_indices)
        if new_dead_idx_len < dead_idx_len:
            assert dead_idx_count > 0
            # 124, 109, 95
    assert len(thou) == 600
    assert thou._dead_index_count == 67

    assert not any([thou[i] is _MISSING for i in range(len(thou))])

    thou &= IndexedSet(range(500, 503))

    assert thou == IndexedSet([501, 502])
    return


def big_popper():
    # more of a benchmark than a test
    from os import urandom
    import time
    big_set = IndexedSet(range(100000))
    rands = [ord(r) for r in urandom(len(big_set))]
    start_time, start_size = time.time(), len(big_set)
    while len(big_set) > 10000:
        if len(big_set) % 10000 == 0:
            print(len(big_set) / 10000)
        rand = rands.pop()
        big_set.pop(rand)
        big_set.pop(-rand)
    end_time, end_size = time.time(), len(big_set)
    print()
    print('popped %s items in %s seconds' % (start_size - end_size,
                                             end_time - start_time))


def test_complement_set():
    '''exercises a bunch of code-paths but doesn't really confirm math identities'''
    assert complement(complement(set())) == set()
    sab = set('ab')
    sbc = set('bc')
    cab = complement('ab')
    cbc = complement('bc')
    cc = complement('c')
    sc = set('c')
    u = complement(set())
    assert repr(sab) in repr(cab)
    # non-mutating tests
    assert cab != cbc
    assert complement(cab) == sab
    assert complement(cbc) == sbc
    assert 'a' not in cab
    assert 'c' in cab
    assert not (cab < sab)  # complement never subset of set
    if not _IS_26: assert not (sab < cab)
    assert not (cbc < sab)
    assert not (cbc < cab)  # not subsets of each other
    if not _IS_26: assert sab < cc
    assert cab < (cab | cbc)
    assert (cab | cbc) > cab
    assert cc > sab
    assert not (cab > sab)
    assert not cab.isdisjoint(cc)  # complements never disjoint
    assert cab.isdisjoint(sab)
    assert not cab.isdisjoint(sc)
    assert (cab | sab) == u
    assert (cab | cc) == u
    assert (cab | cbc) == complement('b')
    assert (sab | cab) == (cbc | sbc)
    assert (sab & cab) == (cbc & sbc)
    assert (sab ^ cab) == (cbc ^ sbc)
    assert cab - cc == sc
    assert cab - sab == cab
    assert (cab ^ cbc | set('b')) == (sab | sbc)
    everything = complement(frozenset())
    assert everything in everything  # https://en.wikipedia.org/wiki/Russell%27s_paradox
    # destructive testing
    cab ^= sab
    cab ^= sab
    cab &= sab
    cab &= cbc
    cab |= sab
    cab |= cbc
    cab -= sab
    cab.add(5)
    cab.remove(5)
    cab.update(sab)
    cab.discard(sab)
    cab.update(cbc)
    cab.add(complement(frozenset()))  # frozen complement can be a member of complement set
    assert len({complement(frozenset()): 1, complement(frozenset()): 2}) == 1  # hash works
    with raises(NotImplementedError): cab.pop()
    with raises(NotImplementedError): len(cab)
    with raises(NotImplementedError): iter(cab)
    ~cab
    cab.complement()
    cab.complemented()
