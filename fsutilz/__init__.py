import typing
from pathlib import Path
import os
from shutil import copy2, copystat
import mmap


class MMap:
	__slots__ = ("path", "f", "m")

	def __init__(self, path: Path):
		self.path = path
		self.f = None
		self.m = None

	def __enter__(self):
		self.f = self.path.open("rb").__enter__()
		self.m = mmap.mmap(self.f.fileno(), 0, prot=mmap.PROT_READ).__enter__()
		return self.m

	def __exit__(self, *args, **kwargs):
		self.m.__exit__(*args, **kwargs)
		self.f.__exit__(*args, **kwargs)


def isGlobPattern(path: typing.Union[Path, str]) -> bool:
	if isinstance(path, str):
		return "*" in path
	else:
		for p in path.parts:
			if "*" in p:
				return True
		return False


def relativePath(src: Path, dst: Path) -> Path:
	src = Path(src).absolute()
	dst = Path(dst).absolute()
	commonPath = Path(os.path.commonpath((src, dst)))
	cpl = len(commonPath.parts)
	up = (".." + os.sep) * (len(dst.parts) - cpl)
	down = os.sep.join(src.parts[cpl - len(src.parts) :])
	return Path(up) / down


def symlink(src: Path, dst: Path, relativeTo: typing.Optional[Path] = None) -> None:
	"""A bit smarter stuff than os.symlink. Can make relative symlinks"""
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
	p = str(p)
	while p[0] == "/":
		p = p[1:]
	res = root / p

	if not isNestedIn(root, res):
		raise Exception("Path is out of root", p, res, root)
	return res


def copytree(src: Path, dst: Path) -> None:
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
	if src.is_dir():
		dst.mkdir(parents=True, exist_ok=True)
		for f in src.iterdir():
			targetName = dst / f.name
			if f.is_dir() and targetName.exists():
				movetree(f, targetName)
				#f.rmdir() #WTF, why is this here?
			else:
				f.rename(targetName)
	else:
		dst.parent.mkdir(parents=True, exist_ok=True)
		src.rename(dst)
