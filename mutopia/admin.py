# -*- coding: utf-8 -*-
from django.contrib import admin

# Register your models here.
from mutopia.models import Style, Composer, Instrument, License, Collection, CollectionPiece
from mutopia.models import Contributor

admin.site.register(Contributor)
admin.site.register(Composer)
admin.site.register(Instrument)
admin.site.register(License)

class CollectionPieceInLine(admin.TabularInline):
    model = CollectionPiece
    extra = 2


class CollectionAdmin(admin.ModelAdmin):
    inlines = [CollectionPieceInLine]


class StyleAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("style",)}

admin.site.register(Collection, CollectionAdmin)
admin.site.register(Style, StyleAdmin)
