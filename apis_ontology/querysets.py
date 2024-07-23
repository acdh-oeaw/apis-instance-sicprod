def SalaryViewSetQueryset(queryset):
    return queryset.filter(typ__in=["Sold", "Provision", "Sonstiges"])
