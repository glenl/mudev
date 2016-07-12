"""The ``models`` module defines the classes for the Django object
   relationship model. Each class represents a table in the underlying
   database, the attributes of a class will represent its columns.
   Methods on each class may be used in templates when rendering web
   pages.

"""
# -*- coding: utf-8 -*-
from django.db import models
import os.path
from mutopia.utils import FTP_URL
from django.utils.text import slugify

class Composer(models.Model):
    """
    A Composer, an author of a piece of music. The methods defined
    here are for use in templates for the web-pages.

    """

    #:The name of the composer. This is specially formatted unique
    #:text that is used as a primary key. The field is built by a
    #:concatenation of the capitalized last name and initials of the
    #:composers given name. For example,
    #:
    #:  * MozartWA
    #:  * BachJS
    #:
    composer = models.CharField(max_length=32, primary_key=True)

    #:A more verbose description, with parenthetic lifespan. The
    #:lifespan data can be omitted in some cases, notably
    #:``Traditional`` and ``Anonymous``.
    description = models.CharField(max_length=48)

    def __str__(self):
        """Returns our internal key for this composer."""
        return self.composer

    def rawstr(self):
        """Return only the full name of the composer."""
        (a,b,c) = self.description.partition('(')
        return a.rstrip()

    def byline(self):
        if self.composer in ['Traditional', 'Anonymous']:
            return self.rawstr()
        else:
            return 'by {0}'.format(self.rawstr())

    class Meta:
        db_table = 'muComposer'
        ordering = ['composer']


class Contributor(models.Model):
    """
    A ``Contributor`` (aka ``Maintainer``) is an entity who
    contributes to the catalog. A user association is not
    maintained by Mutopia so this is not entirely accurate, but it
    allows some normalization for database purposes.

    """

    #:The name of the contributor.
    name = models.CharField(max_length=128, unique=True)

    #:Email address (optional).
    email = models.EmailField(blank=True)

    #:Web or URL entered by the user (optional).
    url = models.URLField(blank=True)

    def __str__(self):
        return self.name

    def reformat_email(self):
        """Munge the email address for display purposes. This is only
        moderately useful against bots...
        """
        if len(self.email) > 0:
            return self.email.replace('@', ' (at) ')
        return self.email

    class Meta:
        db_table = 'muContributor'
        ordering = ['name']


class Style(models.Model):
    """
    A ``Style`` is a genre of music that can be associated with a
    piece.

    """

    #:The name of the style.
    style = models.CharField(max_length=32, primary_key=True)

    #:A slug is a naming mechanism for styles so that URLs are consistent.
    slug = models.SlugField(max_length=32)

    #:Boolean flag to specify whether this style was in the original MutopiaProject.
    in_mutopia = models.BooleanField(default=False)

    @classmethod
    def find_or_create(self, p_style, in_mutopia=False):
        try:
            s = Style.objects.get(style=p_style)
            return s
        except Style.DoesNotExist:
            s = Style.objects.create(style=p_style,
                                     slug=slugify(p_style),
                                     in_mutopia=in_mutopia)
            s.save()
            return s

    def __str__(self):
        return self.style

    class Meta:
        db_table = 'muStyle'
        ordering = ['style']


class LPVersion(models.Model):
    """
    Defines the LilyPond version for a piece of music. These
    versions are defined as a typical ``major.minor.edit``
    string which is broken apart at construction for easier
    manipulation during catalog analysis.

    """

    #:The full string-ified version specification.
    version = models.CharField(max_length=24, unique=True)

    #:Major part of version as integer.
    major = models.IntegerField(blank=True, null=True)

    #:Minor part of version as integer.
    minor = models.IntegerField(blank=True, null=True)

    #:Free-form last part, may contain ASCII characters.
    edit = models.CharField(max_length=8, blank=True)

    @classmethod
    def find_or_create(self, lpversion):
        """Create (or get) the specified LilyPond version.

        :param str lpversion: LilyPond version string
        """
        try:
            v = LPVersion.objects.get(version=lpversion)
            return v
        except LPVersion.DoesNotExist:
            v = LPVersion(version=lpversion)
            bits = lpversion.split('.',2)
            # Expect at least major.minor
            v.major = bits[0]
            v.minor = bits[1]
            # ... but we may not have major.minor.edit
            if len(bits) > 2:
                v.edit = bits[2]
            v.save()
            return v

    def __str__(self):
        return self.version

    class Meta:
        db_table = 'muVersion'


class UpdateMarker(models.Model):
    """
    Used by the update routines, an ``UpdateMarker`` allows the
    last update check to be persistent.

    """

    #:Date of update.
    updated_on = models.DateTimeField()

    def __str__(self):
        return self.updated_on.isoformat()

    class Meta:
        db_table = 'muUpdateMarker'


class Instrument(models.Model):
    """
    An ``Instrument`` defines a single instrument. A boolean flag
    is available to declare whether this instrument was in the
    original Mutopia Instrument list.

    """

    #:The formal unique name of the instrument
    instrument = models.CharField(max_length=32, primary_key=True)

    #:A flag to specify whether this instrument is in the original
    #:collection of Mutopia instruments. This allows the addition of
    #:*unofficial* instrument names.
    in_mutopia = models.BooleanField(default=False)

    def __str__(self):
        return self.instrument

    class Meta:
        db_table = 'muInstrument'
        ordering = ['instrument']


class License(models.Model):
    """
    A ``License`` is a description of the copyright for music in
    the MutopiaProject catalogue. As new licenses emerge, and older
    ones are deprecated, a flag can be set to prevent them from being
    displayed on the licensing page. Inactive licenses may remain for
    as long as necessary.

    """

    #:The name of the license.
    name = models.CharField(max_length=64)

    #:The URL that can be used to lookup extended license information.
    url = models.URLField()

    #:A graphic badge, just the name without extension.
    badge = models.CharField(max_length=32, blank=True)

    #:A flag to declare whether this license is active or not.
    #:Inactive would mean that we are not currently promoting its use
    #:but it is possible that the license is still in use within Mutopia.
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'muLicense'
        ordering = ['name']


class Piece(models.Model):
    """
    A ``Piece`` defines a complete MutopiaProject archive entity. Most
    of the attributes and relationships of this piece are retrieved by
    parsing the header text of a submitted LilyPond file.

    """

    #:Define the unique Mutopia ID for this piece.
    piece_id = models.IntegerField(primary_key=True)

    #:The title of the piece
    title = models.CharField(max_length=128)

    #:The composer is a 1:1 relationship to a specific composer.
    composer = models.ForeignKey(Composer, models.CASCADE)

    #:The style is a 1:1 relationship to a specific style.
    style = models.ForeignKey(Style,
                              models.SET_NULL,
                              blank=True,
                              null=True)

    #:The instrument field in the header can be somewhat free-form so
    #:this is remembered for later parsing and building the
    #:`instruments` relationship.
    raw_instrument = models.TextField(blank=True)

    #:There can only be a single license so this forms a 1:1
    #:relationship to our known licenses.
    license = models.ForeignKey(License,
                                models.SET_NULL,
                                blank=True,
                                null=True)

    #:This field contains the contributor who transcribed the piece.
    maintainer = models.ForeignKey(Contributor,
                                   models.SET_NULL,
                                   blank=True,
                                   null=True)

    #:The LilyPond version that this piece was transcribed with. A 1:1
    #:relationship is formed here to better track pieces done with
    #:specific versions.
    version = models.ForeignKey(LPVersion,
                                models.SET_NULL,
                                blank=True,
                                null=True)

    #:The opus, if any.
    opus = models.CharField(max_length=64, blank=True, default='')

    #:The poet or author of any text associated with the piece.
    lyricist = models.CharField(max_length=128, blank=True, default='')

    #:The composition date if known. It is sometimes approximate and
    #:may contain non-ISO characters.
    date_composed = models.CharField(max_length=32, blank=True)

    #:The publish date is derived from the footer portion of the
    #:header. The full ID can be derived from the ``piece_id`` and
    #:this field.
    date_published = models.DateField()

    #:The source, or publisher, of the piece used to make the
    #:transcription. A text field is used since the name can be quite
    #:long.
    source = models.TextField(blank=True)

    #:The free-form text that a user can apply to a piece.
    moreinfo = models.TextField(blank=True, default='')

    #:Adding instruments as a relationship instead of an attribute
    #:allows a more controlled and accurate search.
    instruments = models.ManyToManyField(Instrument)

    def __str__(self):
        return '{0} - {1}'.format(self.piece_id, self.title)

    class Meta:
        db_table = 'muPiece'


class Collection(models.Model):
    """
    This class defines a collection of associated pieces. This can
    be an entire opus or a other relationship.

    """

    #:A unique description string for this collection. This identifier
    #:is also used to locate an optional info-file on the data store to
    #:display additional user-provided information.
    tag = models.CharField(max_length=32, primary_key=True)

    #:The title of the collection.
    title = models.CharField(max_length=128)

    #:Collections have a M:M relationship with Pieces. A single piece
    #:can belong to more than one collection, a single collection
    #:may contain several pieces.
    pieces = models.ManyToManyField(Piece)

    def user_infofile(self):
        """Return a filename for the optional collection data file."""
        return '/'.join(['collections', self.tag, 'collection-info.dat',])

    def __str__(self):
        return self.tag

    class Meta:
        db_table = 'muCollection'


class AssetMap(models.Model):
    """An ``AssetMap`` forms an association of a single
    :class:`mutopia.models.Piece` to its physical data storage assets. It has
    particular benefit when updating or adding pieces.

    """

    #:The topmost file location for the piece
    folder = models.CharField(max_length=128)

    #:Within a folder, piece assets (pdf files, LilyPond sources,
    #:etc.) can be identified with a single name.
    name = models.CharField(max_length=64, blank=True)

    #:True if this piece uses several LilyPond files.
    has_lys = models.BooleanField(default=False)

    #:The reference to the piece. When new pieces are created this is
    #:left null and filled in when the RDF file is processed.
    piece = models.OneToOneField(Piece,
                                 models.SET_NULL,
                                 blank=True,
                                 null=True)

    def __str__(self):
        return '/'.join([self.folder, self.name,])

    def get_composer(self):
        """Return the composer part of the folder."""
        return self.folder.split('/',1)[0]

    def get_midi(self):
        """Return a full pathname for midi files."""
        return '/'.join([FTP_URL, self.folder, self.midi_spec(),])

    def get_ly(self):
        """Return a full pathname for LilyPond files."""
        return '/'.join([FTP_URL, self.folder, self.ly_spec(),])

    def get_ps_a4(self):
        """Return a full pathname for A4 PostScript files."""
        return '/'.join([FTP_URL, self.folder, self.ps_a4_spec(),])

    def get_ps_let(self):
        """Return a full pathname for Letter PostScript files."""
        return '/'.join([FTP_URL, self.folder, self.ps_let_spec(),])

    def get_pdf_a4(self):
        """Return a full pathname for A4 PDF files."""
        return '/'.join([FTP_URL, self.folder, self.pdf_a4_spec(),])

    def get_pdf_let(self):
        """Return a full pathname for Letter PDF files."""
        return '/'.join([FTP_URL, self.folder, self.pdf_let_spec(),])

    def midi_spec(self):
        """Return a filename for the midi file(s)."""
        if self.has_lys:
            return '{0}-mids.zip'.format(self.name)
        else:
            return '{0}.mid'.format(self.name)

    def ly_spec(self):
        """Return a filename for the LilyPond file(s)."""
        if self.has_lys:
            return '{0}-lys.zip'.format(self.name)
        else:
            return '{0}.ly'.format(self.name)

    def ps_a4_spec(self):
        """Return a filename for the A4 PostScript file(s)."""
        if self.has_lys:
            return '{0}-a4-pss.zip'.format(self.name)
        else:
            return '{0}-a4.ps.gz'.format(self.name)

    def ps_let_spec(self):
        """Return a filename for the Letter PostScript file(s)."""
        if self.has_lys:
            return '{0}-let-pss.zip'.format(self.name)
        else:
            return '{0}-let.ps.gz'.format(self.name)

    def pdf_let_spec(self):
        """Return a filename for the Letter PDF file(s)."""
        if self.has_lys:
            return '{0}-let-pdfs.zip'.format(self.name)
        else:
            return '{0}-let.pdf'.format(self.name)

    def pdf_a4_spec(self):
        """Return a filename for the A4 PDF file(s)."""
        if self.has_lys:
            return '{0}-a4-pdfs.zip'.format(self.name)
        else:
            return '{0}-a4.pdf'.format(self.name)

    class Meta:
        db_table = 'muAssetMap'
        ordering = ['folder']


class RawInstrumentMap(models.Model):
    """
    We want users to specify known instruments in the
    :class:`mutopia.models.Instrument` table but this is not easily regulated with
    user input. The ``RawInstrumentMap`` maps these
    un-regulated names to rows in the :class:`mutopia.models.Instrument` table. This
    table can be used for nicknames (*uke* ==> *ukulele*) as well as
    common misspellings, plurals, or foreign names.

    Only used during RDF processing, not live web code.

    """
    #:An instrument name that may be a nickname (*uke*) or a common
    #:non-English name (*guitarre*) that can be mapped to a name in
    #:the :class:`mutopia.models.Instrument` table.
    raw_instrument = models.TextField(primary_key=True)

    #:Reference to the :class:`mutopia.models.Instrument` table
    instrument = models.ForeignKey(Instrument, models.CASCADE)

    def __str__(self):
        return self.raw_instrument

    class Meta:
        db_table = 'muRawInstrumentMap'
