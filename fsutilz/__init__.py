import mmap
import os
import typing
from pathlib import Path
from shutil import copy2, copystat


class ommap(mmap.mmap):
	"""Our children of `mmap.mmap` that closes its `_parent`"""

	__slots__ = ("parent",)

	def __init__(self, *args, _parent, **kwargs):
		self.parent = _parent

	__init__.__wraps__ = mmap.mmap.__init__

	def __new__(cls, *args, _parent, **kwargs):
		return mmap.mmap.__new__(cls, *args, **kwargs)

	__new__.__wraps__ = mmap.mmap.__new__

	def __exit__(self, *args, **kwargs):
		super().__exit__(*args, **kwargs)
		self.parent.__exit__(*args, **kwargs)


class MMap:
	"""Our class for memory mapping making its usage much easier."""

	__slots__ = ("path", "f", "m")

	def __init__(self, path: Path):
		self.path = path
		self.f = None
		self.m = None

	def __enter__(self):
		self.f = self.path.open("rb").__enter__()
		self.m = ommap(self.f.fileno(), 0, prot=mmap.PROT_READ, _parent=self).__enter__()
		return self.m

	def __exit__(self, *args, **kwargs):
		self.m = None
		if self.f:
			self.f.__exit__(*args, **kwargs)
			self.f = None


def isGlobPattern(path: typing.Union[Path, str]) -> bool:
	"""Returns `True` if the provided `Path` **looks like** a glob pattern (and so requires real globbing)"""

	if isinstance(path, str):
		return "*" in path
	else:
		for p in path.parts:
			if "*" in p:
				return True
		return False


def relativePath(src: Path, dst: Path) -> Path:
	"""Computes one `Path` relative another one"""

	src = Path(src).absolute()
	dst = Path(dst).absolute()
	commonPath = Path(os.path.commonpath((src, dst)))
	cpl = len(commonPath.parts)
	up = (".." + os.sep) * (len(dst.parts) - cpl)
	down = os.sep.join(src.parts[cpl - len(src.parts) :])
	return Path(up) / down


def symlink(src: Path, dst: Path, relativeTo: typing.Optional[Path] = None) -> None:
	"""A bit smarter stuff than `os.symlink`. Can make relative symlinks"""
	if relativeTo is not None:
		relativeFd = os.open(relativeTo, os.O_RDONLY)

		def symlinkerFunc(src, dst):
			return os.symlink(src.relative_to(relativeTo), dst, dir_fd=relativeFd)

	else:
		relativeFd = None
		symlinkerFunc = os.symlink

	dstP = dst.parent
	dstP.mkdir(parents=True, exist_ok=True)

	try:
		if relativeTo:
			try:
				relP = relativePath(src, dstP)
				dstPFd = os.open(dstP, os.O_RDONLY)
				try:
					os.symlink(relP, dst, dir_fd=dstPFd)
				except Exception as ex:
					raise
				finally:
					os.close(dstPFd)
			except Exception as ex:
				symlinkerFunc(src, dst)
		else:
			symlinkerFunc(src, dst)
	except Exception as ex:
		raise
	finally:
		if relativeFd is not None:
			os.close(relativeFd)


def isNestedIn(parent: Path, child: Path) -> bool:
	"""Checks if the `child` `Path` is contained within `parent` path"""

	try:
		parent = parent.absolute().resolve()
		child = child.absolute().resolve().relative_to(parent)

		for p in child.parts:
			if p == "..":
				return False
		return True
	except ValueError as ex:
		return False


def nestPath(root: Path, p: Path) -> Path:
	"""Nests one `Path` into another one. Makes sure that the nested `Path` is contained within `root` path"""

	p = str(p)
	while p[0] == "/":
		p = p[1:]
	res = root / p

	if not isNestedIn(root, res):
		raise Exception("Path is out of root", p, res, root)
	return res


def copytree(src: Path, dst: Path) -> None:
	"""Copies recursively `src` into `dst`."""

	if src.is_dir():
		dst.mkdir(parents=True, exist_ok=True)
		for f in src.iterdir():
			targetName = dst / f.name
			copytree(f, targetName)
	else:
		dst.parent.mkdir(parents=True, exist_ok=True)
		copy2(src, dst, follow_symlinks=False)
		if src.is_symlink():
			assert dst.is_symlink(), dst
		else:
			assert dst.exists(), dst


def movetree(src: Path, dst: Path) -> None:
	"""Moves `src` into `dst`."""

	if src.is_dir():
		dst.mkdir(parents=True, exist_ok=True)
		for f in src.iterdir():
			targetName = dst / f.name
			if f.is_dir() and targetName.exists():
				movetree(f, targetName)
				# f.rmdir() #WTF, why is this here?
			else:
				f.rename(targetName)
	else:
		dst.parent.mkdir(parents=True, exist_ok=True)
		src.rename(dst)
