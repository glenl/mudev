# -*- coding: utf-8 -*-
from django.db import models
import os.path
from mutopia.utils import FTP_URL

class Composer(models.Model):
    composer = models.CharField(max_length=32, primary_key=True)
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
    name = models.CharField(max_length=128, unique=True)
    email = models.EmailField(blank=True)
    url = models.URLField(blank=True)

    def __str__(self):
        return self.name

    def reformat_email(self):
        if len(self.email) > 0:
            return self.email.replace('@', ' (at) ')
        return self.email

    @classmethod
    def find_or_create(self, m_maintainer, m_email, m_url):
        try:
            c = Contributor.objects.get(name=m_maintainer)
            return c
        except Contributor.DoesNotExist:
            c = Contributor(name=m_maintainer, email=m_email, url=m_url)
            c.save()
            return c

    class Meta:
        db_table = 'muContributor'
        ordering = ['name']


class Style(models.Model):
    style = models.CharField(max_length=32, primary_key=True)
    slug = models.SlugField(max_length=32)
    in_mutopia = models.BooleanField(default=False)

    def __str__(self):
        return self.style

    class Meta:
        db_table = 'muStyle'
        ordering = ['style']


class LPVersion(models.Model):
    version = models.CharField(max_length=24, unique=True)
    major = models.IntegerField(blank=True, null=True)
    minor = models.IntegerField(blank=True, null=True)
    edit = models.CharField(max_length=8, blank=True)

    @classmethod
    def find_or_create(self, lpversion):
        try:
            v = LPVersion.objects.get(version=lpversion)
            return v
        except LPVersion.DoesNotExist:
            v = LPVersion(version=lpversion)
            bits = lpversion.split('.',2)
            v.major = bits[0]
            if len(bits) > 1:
                v.minor = bits[1]
                if len(bits) > 2:
                    v.edit = bits[2]
            v.save()
            return v

    def __str__(self):
        return self.version

    class Meta:
        db_table = 'muVersion'


class UpdateMarker(models.Model):
    updated_on = models.DateTimeField()

    def __str__(self):
        return self.updated_on.isoformat()

    class Meta:
        db_table = 'muUpdateMarker'


class Instrument(models.Model):
    instrument = models.CharField(max_length=32, primary_key=True)
    in_mutopia = models.BooleanField(default=False)

    def __str__(self):
        return self.instrument

    class Meta:
        db_table = 'muInstrument'
        ordering = ['instrument']


class License(models.Model):
    name = models.CharField(max_length=64)
    url = models.URLField()
#    short_name = models.CharField(max_length=8)
    badge = models.CharField(max_length=32, blank=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'muLicense'
        ordering = ['name']


class Tag(models.Model):
    name = models.CharField(max_length=32, primary_key=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'muTag'


class Piece(models.Model):
    piece_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=128)
    composer = models.ForeignKey(Composer, models.CASCADE)
    style = models.ForeignKey(Style,
                              models.SET_NULL,
                              blank=True,
                              null=True)
    raw_instrument = models.TextField(blank=True)
    license = models.ForeignKey(License,
                                models.SET_NULL,
                                blank=True,
                                null=True)
    maintainer = models.ForeignKey(Contributor,
                                   models.SET_NULL,
                                   blank=True,
                                   null=True)
    version = models.ForeignKey(LPVersion,
                                models.SET_NULL,
                                blank=True,
                                null=True)
    opus = models.CharField(max_length=64, blank=True, default='')
    lyricist = models.CharField(max_length=128, blank=True, default='')
    date_composed = models.CharField(max_length=32, blank=True)
    date_published = models.DateField()
    source = models.TextField(blank=True)
    moreinfo = models.TextField(blank=True, default='')

    instruments = models.ManyToManyField(Instrument)
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return '{0} - {1}'.format(self.piece_id, self.title)

    class Meta:
        db_table = 'muPiece'


class AssetMap(models.Model):
    """The Asset map holds the physical assets of the piece.
    """
    folder = models.CharField(max_length=128)
    name = models.CharField(max_length=64, blank=True)
    has_lys = models.BooleanField(default=False)
    piece = models.OneToOneField(Piece,
                                 models.SET_NULL,
                                 blank=True,
                                 null=True)

    def __str__(self):
        return '/'.join([self.folder, self.name,])

    def get_composer(self):
        return self.folder.split('/',1)[0]

    def get_midi(self):
        return '/'.join([FTP_URL, self.folder, self.midi_spec(),])

    def get_ly(self):
        return '/'.join([FTP_URL, self.folder, self.ly_spec(),])

    def get_ps_a4(self):
        return '/'.join([FTP_URL, self.folder, self.ps_a4_spec(),])

    def get_ps_let(self):
        return '/'.join([FTP_URL, self.folder, self.ps_let_spec(),])

    def get_pdf_a4(self):
        return '/'.join([FTP_URL, self.folder, self.pdf_a4_spec(),])

    def get_pdf_let(self):
        return '/'.join([FTP_URL, self.folder, self.pdf_let_spec(),])

    def midi_spec(self):
        if self.has_lys:
            return '{0}-mids.zip'.format(self.name)
        else:
            return '{0}.mid'.format(self.name)

    def ly_spec(self):
        if self.has_lys:
            return '{0}-lys.zip'.format(self.name)
        else:
            return '{0}.ly'.format(self.name)

    def ps_a4_spec(self):
        if self.has_lys:
            return '{0}-a4-pss.zip'.format(self.name)
        else:
            return '{0}-a4.ps.gz'.format(self.name)

    def ps_let_spec(self):
        if self.has_lys:
            return '{0}-let-pss.zip'.format(self.name)
        else:
            return '{0}-let.ps.gz'.format(self.name)

    def pdf_let_spec(self):
        if self.has_lys:
            return '{0}-let-pdfs.zip'.format(self.name)
        else:
            return '{0}-let.pdf'.format(self.name)

    def pdf_a4_spec(self):
        if self.has_lys:
            return '{0}-a4-pdfs.zip'.format(self.name)
        else:
            return '{0}-a4.pdf'.format(self.name)

    class Meta:
        db_table = 'muAssetMap'
        ordering = ['folder']


# We want users to specify instruments with our existing tags but that
# does not always happen and there are many legacy cases. This model
# defines a table to map a user's instrument name to our internal
# instrument. This is also a convenient way to implement foreign
# language translations, plurals, local instrument nicknames names
# (e.g., uke->ukulele), etc..
class RawInstrumentMap(models.Model):
    raw_instrument = models.TextField(primary_key=True)
    instrument = models.ForeignKey(Instrument, models.CASCADE)

    def __str__(self):
        return self.raw_instrument

    class Meta:
        db_table = 'muRawInstrumentMap'


class Collection(models.Model):
    tag = models.CharField(max_length=32, primary_key=True)
    title = models.CharField(max_length=128)

    def user_infofile(self):
        """Return a filename for the optional collection data"""
        return os.path.join(['collections', self.tag, 'collection-info.dat'])

    def __str__(self):
        return self.tag

    class Meta:
        db_table = 'muCollection'

class CollectionPiece(models.Model):
    collection = models.ForeignKey(Collection)
    piece = models.ForeignKey(Piece)

    def __str__(self):
        return '{0}, part of {1}'.format(self.piece.title, self.collection.title)

    class Meta:
        db_table = 'muCollectionPiece'
