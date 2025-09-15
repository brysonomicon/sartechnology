import tkinter as tk

class ReorderableListbox(tk.Listbox):
    """A Tkinter Listbox with drag & drop reordering of entries."""
    def __init__(self, master, **kw):
        kw['selectmode'] = tk.SINGLE
        self.update_order_callback = kw.pop('update_order_callback', None)
        self.update_display_callback = kw.pop('update_display_callback', None)
        super().__init__(master, **kw)
        self.bind('<Button-1>', self._select)
        self.bind('<ButtonRelease-1>', self._release)
        self.curIndex = None
        self.dragging = False

    def _select(self, event):
        # Start drag operation
        self.curIndex = self.nearest(event.y)
        self.dragging = True
        self.bind('<Motion>', self._move)

        
    def _release(self, event):
        # Then call the update function
        self.curIndex = None
        # Call the update order callback if provided
        if self.update_order_callback:
            self.update_order_callback()
        
        # Then call the update display callback if provided
        if self.update_display_callback:
            self.update_display_callback()

    def _move(self, event):
        if not self.dragging or self.curIndex is None:
            return
        i = self.nearest(event.y)
        if i < self.curIndex:
            x = self.get(i)
            self.delete(i)
            self.insert(i + 1, x)
            self.curIndex = i
        elif i > self.curIndex:
            x = self.get(i)
            self.delete(i)
            self.insert(i - 1, x)
            self.curIndex = i
