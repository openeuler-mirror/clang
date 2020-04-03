%global maj_ver 7
%global min_ver 0
%global patch_ver 0

%global clang_srcdir cfe-%{version}.src
%global clang_tools_srcdir clang-tools-extra-%{version}.src

Name:		clang
Version:	%{maj_ver}.%{min_ver}.%{patch_ver}
Release:	6
License:	NCSA
Summary:	An "LLVM native" C/C++/Objective-C compiler
URL:		http://llvm.org
Source0:	http://releases.llvm.org/%{version}/%{clang_srcdir}.tar.xz
Source1:	http://llvm.org/releases/%{version}/%{clang_tools_srcdir}.tar.xz
Source100:	clang-config.h

Patch0:		0001-lit.cfg-Add-hack-so-lit-can-find-not-and-FileCheck.patch
Patch1:		0001-GCC-compatibility-Ignore-fstack-clash-protection.patch
Patch2:		0001-Driver-Prefer-vendor-supplied-gcc-toolchain.patch
Patch4:		0001-gtest-reorg.patch
Patch5:		0001-Don-t-prefer-python2.7.patch
Patch6:		0001-Convert-clang-format-diff.py-to-python3-using-2to3.patch
Patch7:		0001-Convert-scan-view-to-python3-using-2to3.patch

BuildRequires:  cmake gcc-c++ python-sphinx git
BuildRequires:	llvm-devel = %{version}
BuildRequires:  compiler-rt = %{version} 
BuildRequires:  llvm-static = %{version}
BuildRequires:	llvm-googletest = %{version}
BuildRequires:	libxml2-devel perl-generators ncurses-devel emacs libatomic
BuildRequires:  python2-lit python3-lit python2-rpm-macros python3-sphinx python3-devel

Requires:	libstdc++-devel gcc-c++ emacs-filesystem
Provides:	clang(major) = %{maj_ver}
Provides:	%{name}-libs = %{version}-%{release}
Obsoletes:	%{name}-libs < %{version}-%{release}
Recommends:     libomp = %{version}

%description
The Clang project provides a language front-end and tooling infrastructure for\
languages in the C language family (C, C++, Objective C/C++, OpenCL, CUDA, and\
RenderScript) for the LLVM project. Both a GCC-compatible compiler driver (clang)\
and an MSVC-compatible compiler driver (clang-cl.exe) are provided.\

%package devel
Summary:	Development header files for clang.
Requires:	%{name} = %{version}-%{release}
Requires:	%{name}-tools-extra = %{version}-%{release}

%description devel
Development header files for clang.

%package        help
Summary:        Help manual for %{name}

%description    help
The %{name}-help package conatins man manual etc

%package analyzer
Summary:	A source code analysis framework
License:	NCSA and MIT
BuildArch:	noarch
Requires:	%{name} = %{version}-%{release}
Requires:	python2

%description analyzer
The Clang Static Analyzer consists of both a source code analysis
framework and a standalone tool that finds bugs in C and Objective-C
programs. The standalone tool is invoked from the command-line, and is
intended to run in tandem with a build of a project or code base.

%package tools-extra
Summary:	Extra tools for clang
Requires:	%{name}-libs = %{version}-%{release}
Requires:	emacs-filesystem

%description tools-extra
A set of extra tools built using Clang's tooling API.

%package -n git-clang-format
Summary:	clang-format integration for git
Requires:	%{name} = %{version}-%{release}
Requires:	git
Requires:	python2

%description -n git-clang-format
clang-format integration for git.

%package -n python2-clang
Summary:	Python2 bindings for clang
Requires:	%{name}-libs = %{version}-%{release}
Requires:	python2
%description -n python2-clang
%{summary}.

%prep
%setup -T -q -b 1 -n %{clang_tools_srcdir}
pathfix.py -i %{__python3} -pn \
	clang-tidy/tool/*.py
pathfix.py -i %{__python2} -pn \
	include-fixer/find-all-symbols/tool/run-find-all-symbols.py

%autosetup -n %{clang_srcdir} -p1 -Sgit
pathfix.py -i %{__python3} -pn \
	tools/clang-format/*.py \
	tools/clang-format/git-clang-format \
	utils/hmaptool/hmaptool \
	tools/scan-view/bin/scan-view
mv ../%{clang_tools_srcdir} tools/extra

%build

mkdir -p _build
cd _build

%ifarch %{arm}
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')
%endif

%cmake .. \
	-DLLVM_LINK_LLVM_DYLIB:BOOL=ON \
	-DCMAKE_BUILD_TYPE=RelWithDebInfo \
	-DLLVM_CONFIG:FILEPATH=/usr/bin/llvm-config-%{__isa_bits} \
	-DCLANG_INCLUDE_TESTS:BOOL=ON \
	-DLLVM_EXTERNAL_LIT=%{_bindir}/lit \
	-DLLVM_MAIN_SRC_DIR=%{_datadir}/llvm/src \
%if 0%{?__isa_bits} == 64
        -DLLVM_LIBDIR_SUFFIX=64 \
%else
        -DLLVM_LIBDIR_SUFFIX= \
%endif
	\
	-DCLANG_ENABLE_ARCMT:BOOL=ON \
	-DCLANG_ENABLE_STATIC_ANALYZER:BOOL=ON \
	-DCLANG_INCLUDE_DOCS:BOOL=ON \
	-DCLANG_PLUGIN_SUPPORT:BOOL=ON \
	-DENABLE_LINKER_BUILD_ID:BOOL=ON \
	-DLLVM_ENABLE_EH=ON \
	-DLLVM_ENABLE_RTTI=ON \
	-DLLVM_BUILD_DOCS=ON \
	-DLLVM_ENABLE_SPHINX=ON \
	-DSPHINX_WARNINGS_AS_ERRORS=OFF \
	\
	-DCLANG_BUILD_EXAMPLES:BOOL=OFF \
	-DCLANG_REPOSITORY_STRING="%{_vendor} %{version}-%{release}" \
	-DLIB_SUFFIX=

%make_build

%install
%make_install -C _build

mkdir -p %{buildroot}%{python2_sitelib}/clang/
install -p -m644 bindings/python/clang/* %{buildroot}%{python2_sitelib}/clang/

mv -v %{buildroot}%{_includedir}/clang/Config/config{,-%{__isa_bits}}.h
install -m 0644 %{SOURCE100} %{buildroot}%{_includedir}/clang/Config/config.h

mkdir -p %{buildroot}%{_emacs_sitestartdir}
for f in clang-format.el clang-rename.el clang-include-fixer.el; do
mv %{buildroot}{%{_datadir}/clang,%{_emacs_sitestartdir}}/$f
done

rm -vf %{buildroot}%{_datadir}/clang/clang-format-bbedit.applescript
rm -vf %{buildroot}%{_datadir}/clang/clang-format-sublime.py*

rm -Rvf %{buildroot}%{_pkgdocdir}

rm -vf %{buildroot}%{_datadir}/clang/bash-autocomplete.sh

ln -s clang++ %{buildroot}%{_bindir}/clang++-%{maj_ver}

%check
cd _build
PATH=%{_libdir}/llvm:$PATH make %{?_smp_mflags} check-clang || \
%ifarch %{arm}
:
%else
false
%endif

%files
%{_bindir}/clang
%{_bindir}/clang++
%{_bindir}/clang-%{maj_ver}
%{_bindir}/clang++-%{maj_ver}
%{_bindir}/clang-check
%{_bindir}/clang-cl
%{_bindir}/clang-cpp
%{_bindir}/clang-format
%{_bindir}/clang-func-mapping
%{_bindir}/clang-import-test
%{_bindir}/clang-offload-bundler
%{_bindir}/diagtool
%{_bindir}/hmaptool
%{_bindir}/c-index-test
%{_emacs_sitestartdir}/clang-format.el
%{_datadir}/clang/clang-format.py*
%{_datadir}/clang/clang-format-diff.py*
%{_libdir}/clang/
%{_libdir}/*.so.*

%files devel
%{_libdir}/*.so
%{_includedir}/clang/
%{_includedir}/clang-c/
%{_libdir}/cmake/*
%dir %{_datadir}/clang/

%files help
%{_mandir}/man1/clang.1.gz
%{_mandir}/man1/diagtool.1.gz

%files analyzer
%{_bindir}/scan-view
%{_bindir}/scan-build
%{_bindir}/scan-build
%{_libexecdir}/ccc-analyzer
%{_libexecdir}/c++-analyzer
%{_datadir}/scan-view/
%{_datadir}/scan-build/
%{_mandir}/man1/scan-build.1.*

%files tools-extra
%{_bindir}/clangd
%{_bindir}/clang-apply-replacements
%{_bindir}/clang-change-namespace
%{_bindir}/clang-include-fixer
%{_bindir}/clang-query
%{_bindir}/clang-refactor
%{_bindir}/clang-reorder-fields
%{_bindir}/clang-rename
%{_bindir}/clang-tidy
%{_bindir}/find-all-symbols
%{_bindir}/modularize
%{_emacs_sitestartdir}/clang-rename.el
%{_emacs_sitestartdir}/clang-include-fixer.el
%{_datadir}/clang/clang-include-fixer.py*
%{_datadir}/clang/clang-tidy-diff.py*
%{_datadir}/clang/run-clang-tidy.py*
%{_datadir}/clang/run-find-all-symbols.py*
%{_datadir}/clang/clang-rename.py*

%files -n git-clang-format
%{_bindir}/git-clang-format

%files -n python2-clang
%{python2_sitelib}/clang/

%changelog
* Fri Apr 03 2020 zhouyihang <zhouyihang1@huawei.com> - 7.0.0-6
- Remove useless scriptlet

* Thu Feb 20 2020 openEuler Buildteam <buildteam@openeuler.org> - 7.0.0-5
- Add buildrequire compiler-rt

* Tue Dec 17 2019 openEuler Buildteam <buildteam@openeuler.org> - 7.0.0-4
- Delete redundant info

* Mon Dec 9 2019 openEuler Buildteam <buildteam@openeuler.org> - 7.0.0-3
- Package init
