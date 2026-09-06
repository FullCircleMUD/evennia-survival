# SPDX-License-Identifier: BSD-3-Clause
"""A consumer's stage module that fails on import — CF-10.

Stands in for any stage module the library cannot load: a typo in the
consumer's own code, a bad import, a member declared without its message
strings. The library refuses either way and chains this error underneath, so
the consumer sees both the setting that is wrong and why.

It lives here rather than in ``tests.py`` because importing it raises, which
is the whole point.
"""

raise RuntimeError("deliberate failure on import — CF-10")
