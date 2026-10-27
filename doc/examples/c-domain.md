# C domain

Field lists of other domains are converted the same way as Python's. This example is
written by hand in MyST:

````{bfl-example}
```{c:function} int clamp(int value, int min, int max)

Clamp a value to a range.

:param value: Value to clamp
:param int min: Lower bound
:param int max: Upper bound
:returns: ``value`` limited to ``[min, max]``
```
````

To only convert the field lists of certain domains, set
{confval}`better_fieldlist_domains`.
