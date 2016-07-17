# -*- coding: utf-8 -*-
"""This modules is used to customize the |django| `Admin` panels.
Models registered with the `Admin` can be created and deleted using
the web UI provided by |django|. This UI can be further manipulated if
necessary.
"""

from django.contrib import admin

# Register your models here.
from mutopia.models import Style, Composer, Instrument, License
from mutopia.models import Contributor, Collection, Piece

# These modifications allows an existing Collection to be assigned
# when editing a Piece.
class PieceInline(admin.TabularInline):
    model = Collection.pieces.through

class PieceAdmin(admin.ModelAdmin):
    inlines = [
        PieceInline,
    ]


# The pieces list is difficult to edit so it is replaced with the
# inline notation
class CollectionAdmin(admin.ModelAdmin):
    inlines = [
        PieceInline,
    ]
    exclude = ('pieces',)


class StyleAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("style",)}


admin.site.register(Contributor)
admin.site.register(Composer)
admin.site.register(Instrument)
admin.site.register(License)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Piece, PieceAdmin)
admin.site.register(Style, StyleAdmin)
