# %%global toolchain clang

%global maj_ver 15
%global min_ver 0
%global patch_ver 7
%global clang_srcdir clang-%{version}.src
%global clang_tools_srcdir clang-tools-extra-%{version}.src

Name:		clang
Version:	15.0.7
Release:	1
License:	GPL-2.0-only and Apache-2.0 and MIT
Summary:	An "LLVM native" C/C++/Objective-C compiler
URL:		http://llvm.org
Source0:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{version}/%{clang_srcdir}.tar.xz
Source1:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{version}/%{clang_tools_srcdir}.tar.xz
Source2:	clang-config.h

# Note: Can be dropped in LLVM 16: https://reviews.llvm.org/D133316
Patch1:		0001-Mark-fopenmp-implicit-rpath-as-NoArgumentUnused.patch
# Patches for clang-tools-extra
# See https://reviews.llvm.org/D120301
Patch201:	0001-clang-tools-extra-Make-test-dependency-on-LLVMHello-.patch

BuildRequires:	cmake ninja-build gcc-g++ python-sphinx git
BuildRequires:	llvm-devel = %{version}
BuildRequires:  llvm-static = %{version}
BuildRequires:	llvm-googletest = %{version}
BuildRequires:	libxml2-devel perl-generators ncurses-devel emacs libatomic
BuildRequires:  python3-lit python3-sphinx python3-devel python3-recommonmark


Requires:	libstdc++-devel gcc-c++ emacs-filesystem
Requires:	%{name}-resource-filesystem = %{version}
Provides:	clang(major) = %{maj_ver}
Provides:	%{name}-libs = %{version}-%{release}
Obsoletes:	%{name}-libs < %{version}-%{release}
Recommends:     libomp = %{version}
Recommends:     compiler-rt = %{version}

Conflicts:      compiler-rt < %{version}
Conflicts:      compiler-rt > %{version}

%ifnarch riscv64
Patch2:		support-ignored_and_replaced_opts.patch
Patch3:		support-print-c-function-prototype.patch
%endif

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

%package resource-filesystem
Summary: Filesystem package that owns the clang resource directory
Provides: %{name}-resource-filesystem(major) = %{maj_ver}

%description resource-filesystem
This package owns the clang resouce directory: $libdir/clang/$version/

%package        help
Summary:        Help manual for %{name}

%description    help
The %{name}-help package conatins man manual etc

%package analyzer
Summary:	A source code analysis framework
License:	NCSA and MIT
BuildArch:	noarch
Requires:	%{name} = %{version}-%{release}
Requires:	python3

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

%description -n git-clang-format
clang-format integration for git.

%prep
%setup -T -q -b 1 -n %{clang_tools_srcdir}
%autopatch -m200 -p2

# failing test case
rm test/clang-tidy/checkers/altera/struct-pack-align.cpp

pathfix.py -i %{__python3} -pn \
	clang-tidy/tool/*.py \
	clang-include-fixer/find-all-symbols/tool/run-find-all-symbols.py

%setup -q -n %{clang_srcdir}
%autopatch -M200 -p2

# failing test case
rm test/CodeGen/profile-filter.c

pathfix.py -i %{__python3} -pn \
	tools/clang-format/*.py \
	tools/clang-format/git-clang-format \
	utils/hmaptool/hmaptool \
	tools/scan-view/bin/scan-view \
	tools/scan-view/share/Reporter.py \
	tools/scan-view/share/startfile.py \
	tools/scan-build-py/bin/* \
	tools/scan-build-py/libexec/*
mv ../%{clang_tools_srcdir} tools/extra

%build

mkdir -p _build
cd _build

%set_build_flags
CXXFLAGS="$CXXFLAGS -Wno-address -Wno-nonnull -Wno-maybe-uninitialized"
CFLAGS="$CFLAGS -Wno-address -Wno-nonnull -Wno-maybe-uninitialized"

%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')

%ifarch riscv64
LDFLAGS+=" -latomic"
%endif

%cmake .. \
	-DLLVM_PARALLEL_LINK_JOBS=1 \
	-DLLVM_LINK_LLVM_DYLIB:BOOL=ON \
	-DCMAKE_BUILD_TYPE=RelWithDebInfo \
	-DCMAKE_INSTALL_RPATH:BOOL=";" \
	-DCMAKE_C_FLAGS_RELWITHDEBINFO="%{optflags} -DNDEBUG" \
	-DCMAKE_CXX_FLAGS_RELWITHDEBINFO="%{optflags} -DNDEBUG" \
	-DLLVM_CONFIG:FILEPATH=/usr/bin/llvm-config-%{__isa_bits} \
	-DCLANG_INCLUDE_TESTS:BOOL=ON \
	-DLLVM_BUILD_UTILS:BOOL=ON \
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

# install scanbuild-py to python sitelib.
mkdir -p %{buildroot}%{python3_sitelib}
mv %{buildroot}%{_prefix}/lib/{libear,libscanbuild} %{buildroot}%{python3_sitelib}
%py_byte_compile %{__python3} %{buildroot}%{python3_sitelib}/libear
%py_byte_compile %{__python3} %{buildroot}%{python3_sitelib}/libscanbuild

mv -v %{buildroot}%{_includedir}/clang/Config/config{,-%{__isa_bits}}.h
install -m 0644 %{SOURCE2} %{buildroot}%{_includedir}/clang/Config/config.h

# Fix permissions of scan-view scripts
chmod a+x %{buildroot}%{_datadir}/scan-view/{Reporter.py,startfile.py}

mkdir -p %{buildroot}%{_emacs_sitestartdir}
for f in clang-format.el clang-rename.el clang-include-fixer.el; do
mv %{buildroot}{%{_datadir}/clang,%{_emacs_sitestartdir}}/$f
done

rm -vf %{buildroot}%{_datadir}/clang/clang-format-bbedit.applescript
rm -vf %{buildroot}%{_datadir}/clang/clang-format-sublime.py*

rm -Rvf %{buildroot}%{_pkgdocdir}

rm -vf %{buildroot}%{_datadir}/clang/bash-autocomplete.sh

# Create sub-directories in the clang resource directory that will be
# populated by other packages
mkdir -p %{buildroot}%{_libdir}/clang/%{version}/{include,lib,share}/

# Remove clang-tidy headers.  
rm -Rvf %{buildroot}%{_includedir}/clang-tidy/

ln -s clang++ %{buildroot}%{_bindir}/clang++-%{maj_ver}

%check
# Checking is disabled because we don't pack libLLVMTestingSupport.a, which makes
# standalone build of clang impossible.

#cd _build
#PATH=%{_libdir}/llvm:$PATH make %{?_smp_mflags} check-clang || \
#%ifarch %{arm}
#:
#%else
#false
#%endif

%post
/sbin/ldconfig

%postun
/sbin/ldconfig

%files
%{_bindir}/clang
%{_bindir}/clang++
%{_bindir}/clang-%{maj_ver}
%{_bindir}/clang++-%{maj_ver}
%{_bindir}/clang-check
%{_bindir}/clang-cl
%{_bindir}/clang-cpp
%{_bindir}/clang-format
%{_bindir}/clang-doc
%{_bindir}/clang-extdef-mapping
%{_bindir}/clang-move
%{_bindir}/clang-offload-wrapper
%{_bindir}/clang-scan-deps
%{_bindir}/pp-trace
%{_bindir}/clang-offload-bundler
%{_bindir}/clang-offload-packager
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
# %{_bindir}/clang-tblgen
%dir %{_datadir}/clang/

%files resource-filesystem
%dir %{_libdir}/clang/%{version}/
%dir %{_libdir}/clang/%{version}/include/
%dir %{_libdir}/clang/%{version}/lib/
%dir %{_libdir}/clang/%{version}/share/

%files help
%{_mandir}/man1/clang.1.gz
%{_mandir}/man1/diagtool.1.gz
%{_docdir}/Clang/clang/html

%files analyzer
%{_bindir}/scan-view
%{_bindir}/scan-build
%{_bindir}/analyze-build
%{_bindir}/intercept-build
%{_bindir}/scan-build-py
%{_libexecdir}/ccc-analyzer
%{_libexecdir}/c++-analyzer
%{_libexecdir}/analyze-c++
%{_libexecdir}/analyze-cc
%{_libexecdir}/intercept-c++
%{_libexecdir}/intercept-cc
%{_datadir}/scan-view/
%{_datadir}/scan-build/
%{_mandir}/man1/scan-build.1.*
%{python3_sitelib}/libear
%{python3_sitelib}/libscanbuild

%files tools-extra
%{_bindir}/clangd
%{_bindir}/clang-apply-replacements
%{_bindir}/clang-change-namespace
%{_bindir}/clang-include-fixer
%{_bindir}/clang-linker-wrapper
%{_bindir}/clang-nvlink-wrapper
%{_bindir}/clang-pseudo
%{_bindir}/clang-query
%{_bindir}/clang-refactor
%{_bindir}/clang-reorder-fields
%{_bindir}/clang-rename
%{_bindir}/clang-repl
%{_bindir}/clang-tidy
%{_bindir}/find-all-symbols
%{_bindir}/modularize
%{_emacs_sitestartdir}/clang-rename.el
%{_emacs_sitestartdir}/clang-include-fixer.el
%{_datadir}/clang/clang-include-fixer.py*
%{_datadir}/clang/clang-tidy-diff.py*
%{_bindir}/run-clang-tidy
%{_datadir}/clang/run-find-all-symbols.py*
%{_datadir}/clang/clang-rename.py*
%{_datadir}/clang/index.js
%{_datadir}/clang/clang-doc-default-stylesheet.css

%files -n git-clang-format
%{_bindir}/git-clang-format

%changelog
* Fri Mar 24 2023 jchzhou <zhoujiacheng@iscas.ac.cn> - 15.0.7-2
- Fix patch number conflict

* Thu Jan 12 2023 jchzhou <zhoujiacheng@iscas.ac.cn> - 15.0.7-1
- Update to 15.0.7

* Fri Jul 15 2022 jchzhou <zhoujiacheng@iscas.ac.cn> - 14.0.5-1
- Update to 14.0.5

* Tue Nov 29 2022 jchzhou <zhoujiacheng@iscas.ac.cn> - 13.0.1-1
- Update to 13.0.1
- With temp fix of riscv64 libatomic ld flag from @wangyangdahai

* Thu Sep 22 2022 linguoxiong <cokelin@hnu.edu.cn> - 12.0.1-3
- Implement the "-aux-info" option to print function prototype

* Tue Aug 23 2022 linguoxiong <cokelin@hnu.edu.cn> - 12.0.1-2
- Implement some options to ignore and replace

* Wed Dec 29 2021 panxiaohe <panxiaohe@huawei.com> - 12.0.1-1
- update to 12.0.1
- add clang-resource-filesystem sub-package

* Tue Sep 07 2021 chenchen <chen_aka_jan@163.com> - 10.0.1-5
- del rpath from some binaries and bin

* Fri Apr 30 2021 licihua <licihua@huawei.com> - 10.0.1-4
- Reduce build time.

* Thu Apr 29 2021 licihua <licihua@huawei.com> - 10.0.1-3
- Reduce debuginfo verbosity.

* Thu Feb 18 2021 zhangjiapeng <zhangjiapeng9@huawei.com> - 10.0.1-2
- Modify the dependency to python3

* Fri Sep 25 2020 zhangjiapeng <zhangjiapeng9@huawei.com> - 10.0.1-1
- Delete low version dynamic library

* Thu Jul 30 2020 Guoshuai Sun <sunguoshuai> - 10.0.1-0
- Upgrade to 10.0.1

* Thu May 28 2020 leiju <leiju4@huawei.com> - 7.0.0-7
- Fix uninitialized value in ABIArgInfo

* Fri Apr 03 2020 zhouyihang <zhouyihang1@huawei.com> - 7.0.0-6
- Remove useless scriptlet

* Thu Feb 20 2020 openEuler Buildteam <buildteam@openeuler.org> - 7.0.0-5
- Add buildrequire compiler-rt

* Tue Dec 17 2019 openEuler Buildteam <buildteam@openeuler.org> - 7.0.0-4
- Delete redundant info

* Mon Dec 9 2019 openEuler Buildteam <buildteam@openeuler.org> - 7.0.0-3
- Package init
