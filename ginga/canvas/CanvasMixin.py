#
# CanvasMixin.py -- enable canvas like capabilities.
#
# Eric Jeschke (eric@naoj.org)
#
# Copyright (c) Eric R. Jeschke.  All rights reserved.
# This is open-source software licensed under a BSD license.
# Please see the file LICENSE.txt for details.
#
from ginga.canvas.CompoundMixin import CompoundMixin
from ginga.util.six.moves import map, filter

class CanvasError(Exception):
    pass

class CanvasMixin(object):
    """A CanvasMixin is combined with the CompoundMixin to make a
    tag-addressible canvas-like interface.  This mixin should precede the
    CompoundMixin in the inheritance (and so, method resolution) order.
    """

    def __init__(self):
        assert isinstance(self, CompoundMixin), "Missing CompoundMixin class"
        # holds the list of tags
        self.tags = {}
        self.count = 0

        for name in ('modified', ):
            self.enable_callback(name)

    def update_canvas(self, whence=3):
        # TODO: deprecate?
        self.make_callback('modified', whence)

    def redraw(self, whence=3):
        self.make_callback('modified', whence)

    def subcanvas_updated_cb(self, canvas, whence):
        """
        This is a notification that a subcanvas (a canvas contained in
        our canvas) has been modified.  We in turn signal that our canvas
        has been modified.
        """
        # avoid self-referential loops
        if canvas != self:
            #print("%s subcanvas %s was updated" % (self.name, canvas.name))
            self.make_callback_nochildren('modified', whence)

    def add(self, obj, tag=None, tagpfx=None, belowThis=None, redraw=True):
        self.count += 1
        if tag:
            # user supplied a tag
            if tag in self.tags:
                raise CanvasError("Tag already used: '%s'" % (tag))
        else:
            if tagpfx:
                # user supplied a tag prefix
                if tagpfx.startswith('@'):
                    raise CanvasError("Tag prefix may not begin with '@'")
                tag = '%s%d' % (tagpfx, self.count)
            else:
                # make up our own tag
                tag = '@%d' % (self.count)

        obj.tag = tag
        self.tags[tag] = obj
        self.addObject(obj, belowThis=belowThis)

        # propagate change notification on this canvas
        if obj.has_callback('modified'):
            obj.add_callback('modified', self.subcanvas_updated_cb)

        if redraw:
            self.update_canvas(whence=3)
        return tag

    def deleteObjectsByTag(self, tags, redraw=True):
        for tag in tags:
            try:
                obj = self.tags[tag]
                del self.tags[tag]
                super(CanvasMixin, self).deleteObject(obj)
            except Exception as e:
                continue

        if redraw:
            self.update_canvas(whence=3)

    def deleteObjectByTag(self, tag, redraw=True):
        self.deleteObjectsByTag([tag], redraw=redraw)

    def getObjectByTag(self, tag):
        obj = self.tags[tag]
        return obj

    def lookup_object_tag(self, obj):
        # TODO: we may need to have a reverse index eventually
        for tag, ref in self.tags.items():
            if ref == obj:
                return tag
        return None

    def getTagsByTagpfx(self, tagpfx):
        res = []
        keys = filter(lambda k: k.startswith(tagpfx), self.tags.keys())
        return keys

    def getObjectsByTagpfx(self, tagpfx):
        return list(map(lambda k: self.tags[k], self.getTagsByTagpfx(tagpfx)))

    def deleteAllObjects(self, redraw=True):
        self.tags = {}
        CompoundMixin.deleteAllObjects(self)

        if redraw:
            self.update_canvas(whence=3)

    def deleteObjects(self, objects, redraw=True):
        for tag, obj in self.tags.items():
            if obj in objects:
                self.deleteObjectByTag(tag, redraw=False)

        if redraw:
            self.update_canvas(whence=3)

    def deleteObject(self, obj, redraw=True):
        self.deleteObjects([obj], redraw=redraw)

    def raiseObjectByTag(self, tag, aboveThis=None, redraw=True):
        obj1 = self.getObjectByTag(tag)
        if not aboveThis:
            self.raiseObject(obj1)
        else:
            obj2 = self.getObjectByTag(aboveThis)
            self.raiseObject(obj1, obj2)

        if redraw:
            self.update_canvas(whence=3)

    def lowerObjectByTag(self, tag, belowThis=None, redraw=True):
        obj1 = self.getObjectByTag(tag)
        if not belowThis:
            self.lowerObject(obj1)
        else:
            obj2 = self.getObjectByTag(belowThis)
            self.lowerObject(obj1, obj2)

        if redraw:
            self.update_canvas(whence=3)


#END
