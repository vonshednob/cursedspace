# Changelog

This file contains the changes made between released versions.

The format is based on [Keep a changelog](https://keepachangelog.com/) and the versioning tries to follow
[Semantic Versioning](https://semver.org).

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

