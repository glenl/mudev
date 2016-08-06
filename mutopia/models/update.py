"""These are database update-related model for the |django| ORM. In
particular, the :class:`mutopia.models.AssetMap` is of interest
because it additionally functions to translate objects of type
:class:`mutopia.models.Piece` to the physical assets on the the
storage server.

.. moduleauthor:: Glen Larsen, glenl.glx at gmail.com

"""

from django.db import models
from mutopia.utils import FTP_URL
from .models import Piece

class UpdateMarker(models.Model):
    """A persistent timestamp.

    Provides for storage of an timestamp to be used by the update
    process.

    """

    #:Date of update.
    updated_on = models.DateTimeField()

    def __str__(self):
        return self.updated_on.isoformat()

    class Meta:
        db_table = 'muUpdateMarker'


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
        return self.folder.split('/', 1)[0]

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
