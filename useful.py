#!/usr/bin/python
def SelectAddress(name, mask, lastknown='/media/matterwave/David/python scripts/addresses.list'):
        """Given an instrument name and a mask describing the valid options, provide an interactive menu for the user to select the address.

        Example: SelectAddress("Thorlabs Power Meter", "/dev/ttyUSB*")

        If no addresses match the mask, then an error is returned. If the named instrument has a previously known address (stored in addresses.list), then set that as default. The last known address is updated once the user selects an address."""
        
        # Create a list of available choices from the given mask
        from glob import glob
        choices = glob(mask)[::-1]
        if len(choices) == 0:
                raise Exception('No valid addresses found for [%s] using mask [%s]' % (name, mask))

        # Find the last know address for this named device
        lines = [line.strip() for line in open(lastknown).readlines()]
        addresses = dict()
        for line in lines:
                (n,v) = line.split('\t')
                addresses[n] = v

        # If this named device is known, then check whether the last known address is still a valid choice; if it is, move it to the top of the list
        try:
		choices.remove(addresses[name])
		choices.insert(0, addresses[name])
        except KeyError:
                print "Named instrument [%s] has no last known address" % name
        except ValueError:
                print "Named instrument [%s]: last known address [%s] is no longer valid" % (name, addresses[name])
        
        # Use a curses-based menu system to allow the user to select a device
        # Lifted from urwid "Simple Menu" example and hacked in a very un-pythonic way to return a value
        # http://excess.org/urwid/docs/tutorial/
	class storeValue:
		def __init__(self, value):
			self.value = value
	choiceObj = storeValue(None)

        import urwid
        def menu(title, choices):
            body = [urwid.Text(title), urwid.Divider()]
            for c in choices:
                button = urwid.Button(c)
                urwid.connect_signal(button, 'click', item_chosen, c)
                body.append(urwid.AttrMap(button, None, focus_map='reversed'))
            return urwid.ListBox(urwid.SimpleFocusListWalker(body))

        def item_chosen(button, c):
            choiceObj.value = c
            raise urwid.ExitMainLoop()

        main = urwid.Padding(menu(u'Select address for %s' % name, choices), left=2, right=2)
        top = urwid.Overlay(main,
                            urwid.SolidFill(u'\N{MEDIUM SHADE}'), align='center', width=('relative', 90),
			    valign='middle', height=('relative', 90),  min_width=20, min_height=9)

        tmp = urwid.MainLoop(top, palette=[('reversed', 'standout', '')]).run()
	choice = choiceObj.value

        # Save this as the last known address
        addresses[name] = choice
	try:
		h = open(lastknown, 'w')
		for key, value in addresses.iteritems():
			h.write('%s\t%s\n' % (key, value))
		h.close()
	except:
		raise Warning("Unable to update last known address!")

        return choice

def countdown(t=10):
	from time import sleep
	while t!=0:
		print t
		t-=1
		sleep(1)
