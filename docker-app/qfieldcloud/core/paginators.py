import inspect

from django.core.paginator import Paginator
from django.db import connection
from django.utils.functional import cached_property
from django.utils.inspect import method_has_no_args


class LargeTablePaginator(Paginator):
    """
    Only for Postgres:
    Overrides the count method to get an estimate instead of actual count when not filtered
    inspired by: https://djangosnippets.org/snippets/2855/
    """

    EXACT_COUNT_LIMIT = 10000

    @cached_property
    def count(self):
        """
        Returns the total number of objects, across all pages.
        Changed to use an estimate if the estimate is greater than EXACT_COUNT_LIMIT
        """
        c = getattr(self.object_list, "count", None)
        if callable(c) and not inspect.isbuiltin(c) and method_has_no_args(c):
            estimate = 0
            if not self.object_list.query.where:
                try:
                    cursor = connection.cursor()
                    cursor.execute(
                        "SELECT reltuples FROM pg_class WHERE relname = %s",
                        [self.object_list.query.model._meta.db_table],
                    )
                    estimate = int(cursor.fetchone()[0])
                except:  # noqa: E722
                    pass
            if estimate < self.EXACT_COUNT_LIMIT:
                return c()
            else:
                return estimate
        return len(self.object_list)
