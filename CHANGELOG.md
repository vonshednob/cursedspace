# Changelog

This file contains the changes made between released versions.

The format is based on [Keep a changelog](https://keepachangelog.com/) and the versioning tries to follow
[Semantic Versioning](https://semver.org).

## 1.4.0

### Fixed
- All combinations of borders now draws correctly in `Panel`
- Readme example missing import

### Added
- `Grid` class that handles a set of `Panel`s spanning any set of cells in a rectangular grid
- `ProgressBar` panel to show the value of a variable graphically, allows a description
- Folder of example usage
- `Panel` constructor now takes `border` as an argument as well

## 1.3.1
### Fixed
- ScrollPanel shifted the entire list by -1

## 1.3.0
### Added
- Panel has a `BORDER_STYLE` that can be used to have a differently styled border
- Panel has a `content_area` function that indicates the dimensions of the area inside the border (if any)

### Changed
- ScrollPanel clears the space below the last item and the bottom of the panel, even when `clear` is `False`

### Fixed
- Terminals are no longer in a broken state when closing the application

## 1.2.2
### Fixed
- Stray logging statement caused crash

## 1.2.1
### Fixed
- Once more a fix for the scrolling behaviour when the available space for the list is smaller than the scroll margin

## 1.2.0
### Added
- Basic autocompletion support for InputLine through the Completion class

### Fixed
- `do_paint_item` of ScrollPanel would tell that the window is one cell to narrow (maxwidth-1). It does no longer, but that also means you have to `try ... catch curses.error` if you draw into the right-most cell.

## 1.1.0
### Added
- `InputLine` has a `read_only` property
- Optional parameter to `ShellContext` to clear before entering
- `Application` has a `show_cursor` function and restores cursor state upon
  exit
- `Application` has a `set_term_title` function
- `Application` clears the screen upon exit
- `ScrollPanel` has a convenience `jump_to` function
- `ShellContext` clears and restores cursor state

### Fixed
- `InputLine` did not call `noutrefresh` during painting which could leave the
  input line emtpy after painting
- `InputLine` returns cursor coordinates of `focus` call
- A potential crash when `scrollpanel.move` was called
- Use terminal default for the `DEFAULT` color pair
- Prevent painting of items outside the visible range of the `ScrollPanel`


## 1.0.0 -- previously called 0.2.0
### Breaking Change
- `colors` component has been refactored and is incompatible with the previous API

## 0.1.2
### Added
- Various bits of documentation
- Support for basic navigation keys in `InputLine`
- Support for PageUp and PageDown in `ScrollPanel`
- Optional background for `InputLine` (e.g. ░ instead of blank space)
- `Colors.BLACK` and `Colors.WHITE`
- `Panel.focus` returns the coordinates of the cursor

### Changed
- `ScrollPanel` moves the cursor to the current item upon `focus`
- `Application` returns 0 upon successful exit

### Fixed
- Ensure cursor is always inside the text/window of `InputLine` and `ScrollPanel` upon scrolling
- Scrolling behaviour of `ScrollPanel` contained a auto-scrolling bug when the list of item was just short of the available height

## 0.1.1
### Added
- `ShellContext` for execution of subprocesses outside of the curses context
- `ScrollPanel`, a convenient wrapper for scrolling through lists of items in a panel


## 0.1.0
- Initial release

