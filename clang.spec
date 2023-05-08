%global maj_ver 12
%global min_ver 0
%global patch_ver 1

%global clang_version %{maj_ver}.%{min_ver}.%{patch_ver}
%global pkg_name clang%{maj_ver}
%global bin_suffix -%{maj_ver}
%global install_prefix %{_libdir}/llvm%{maj_ver}
%global install_bindir %{install_prefix}/bin
%global install_includedir %{install_prefix}/include
%global install_libdir %{install_prefix}/lib
%global install_libexecdir %{install_prefix}/libexec
%global install_sharedir %{install_prefix}/share
%global install_docdir %{install_sharedir}/doc

%global pkg_bindir %{install_bindir}
%global pkg_includedir %{install_includedir}
%global pkg_libdir %{install_libdir}
%global pkg_libexecdir %{install_libexecdir}
%global pkg_sharedir %{install_sharedir}
%global pkg_docdir %{install_sharedir}/doc

%global clang_srcdir clang-%{version}.src
%global clang_tools_srcdir clang-tools-extra-%{version}.src

Name:		%pkg_name
Version:	%{clang_version}
Release:	4
License:	GPL-2.0-only and Apache-2.0 and MIT
Summary:	An "LLVM native" C/C++/Objective-C compiler
URL:		http://llvm.org
Source0:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{clang_version}/%{clang_srcdir}.tar.xz
Source1:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{clang_version}/%{clang_tools_srcdir}.tar.xz
Source2:	clang-config.h

BuildRequires:  cmake gcc-c++ python-sphinx git
BuildRequires:	llvm%{maj_ver}-devel = %{version}
BuildRequires:	llvm%{maj_ver}-static = %{version}
BuildRequires:	llvm%{maj_ver}-test = %{version}
BuildRequires:	llvm%{maj_ver}-googletest = %{version}
BuildRequires:	libxml2-devel perl-generators ncurses-devel emacs libatomic
BuildRequires:  python3-lit python3-sphinx python3-devel


Requires:	libstdc++-devel gcc-c++ emacs-filesystem
Requires:	%{name}-resource-filesystem = %{version}
Provides:	clang(major) = %{maj_ver}
Provides:	%{name}-libs = %{version}-%{release}
Obsoletes:	%{name}-libs < %{version}-%{release}
Recommends:     libomp = %{version}
Recommends:     compiler-rt = %{version}

Conflicts:      compiler-rt < %{version}
Conflicts:      compiler-rt > %{version}

Patch0:		support-ignored_and_replaced_opts.patch
Patch1:		support-print-c-function-prototype.patch

%description
The Clang project provides a language front-end and tooling infrastructure for\
languages in the C language family (C, C++, Objective C/C++, OpenCL, CUDA, and\
RenderScript) for the LLVM project. Both a GCC-compatible compiler driver (clang)\
and an MSVC-compatible compiler driver (clang-cl.exe) are provided.\

%package libs
Summary: Runtime library for clang
Requires: %{name}-resource-filesystem%{?_isa} = %{version}
Recommends: compiler-rt%{?_isa} = %{version}
Recommends: libatomic%{?_isa}
Recommends: libomp-devel%{_isa} = %{version}
Recommends: libomp%{_isa} = %{version}

%description libs
Runtime library for clang.

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
Requires:	%{name}-libs%{?_isa} = %{version}-%{release}
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
pathfix.py -i %{__python3} -pn \
	clang-tidy/tool/*.py

%autosetup -n %{clang_srcdir} -p1
pathfix.py -i %{__python3} -pn \
	tools/clang-format/*.py \
	tools/clang-format/git-clang-format \
	utils/hmaptool/hmaptool \
	tools/scan-view/bin/scan-view
mv ../%{clang_tools_srcdir} tools/extra

%build

mkdir -p _build
cd _build


%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')


%cmake .. \
	-DLLVM_LINK_LLVM_DYLIB:BOOL=ON \
	-DCMAKE_BUILD_TYPE=RelWithDebInfo \
	-DCMAKE_INSTALL_RPATH:BOOL=";" \
	-DCMAKE_C_FLAGS_RELWITHDEBINFO="%{optflags} -DNDEBUG" \
	-DCMAKE_CXX_FLAGS_RELWITHDEBINFO="%{optflags} -DNDEBUG" \
	-DLLVM_CONFIG:FILEPATH=%{pkg_bindir}/llvm-config-%{maj_ver}-%{__isa_bits} \
	-DCLANG_INCLUDE_TESTS:BOOL=ON \
	-DLLVM_EXTERNAL_LIT=%{_bindir}/lit \
	-DLLVM_MAIN_SRC_DIR=%{_libdir}/llvm%{maj_ver}/src \
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
	-DCMAKE_INSTALL_PREFIX=%{install_prefix} \
	-DCLANG_BUILD_EXAMPLES:BOOL=OFF \
	-DCLANG_REPOSITORY_STRING="%{?distro} %{version}-%{release}" \
	-DLIB_SUFFIX=

%make_build

%install
%make_install -C _build

mkdir -p %{buildroot}%{_includedir}/clang/Config/
# install -m 0644 %{SOURCE2} %{buildroot}%{_includedir}/clang/Config/config.h

mkdir -p %{buildroot}%{_emacs_sitestartdir}
for f in clang-format.el clang-rename.el clang-include-fixer.el; do
mv %{buildroot}{%{install_sharedir}/clang,%{_emacs_sitestartdir}}/$f
done

rm -vf %{buildroot}%{install_sharedir}/clang/clang-format-bbedit.applescript
rm -vf %{buildroot}%{install_sharedir}/clang/clang-format-sublime.py*
rm -Rvf %{buildroot}%{install_docdir}/clang/html

rm -Rvf %{buildroot}%{_pkgdocdir}

rm -vf %{buildroot}%{install_sharedir}/clang/bash-autocomplete.sh

mkdir -p %{buildroot}%{_bindir}
for f in %{buildroot}/%{install_bindir}/*; do
  filename=`basename $f`
  if [ $filename != "clang%{bin_suffix}" ]; then
      ln -s ../../%{install_bindir}/$filename %{buildroot}%{_bindir}/$filename%{bin_suffix}
  fi
done

# Create Manpage symlinks
mkdir -p %{buildroot}%{_mandir}/man1
for f in %{buildroot}%{install_prefix}/share/man/man1/*; do
  filename=`basename $f | cut -f 1 -d '.'`
  mv $f %{buildroot}%{_mandir}/man1/$filename%{bin_suffix}.1
done

# Create sub-directories in the clang resource directory that will be
# populated by other packages
mkdir -p %{buildroot}%{pkg_libdir}/clang/%{version}/{include,lib,share}/

# Remove clang-tidy headers.  
rm -Rvf %{buildroot}%{install_includedir}/clang-tidy/

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
%{_bindir}/clang-%{maj_ver}
%{_bindir}/clang++-%{maj_ver}
%{_bindir}/clang-check%{bin_suffix}
%{_bindir}/clang-cl-%{maj_ver}
%{_bindir}/clang-cpp-%{maj_ver}
%{_bindir}/clang-format%{bin_suffix}
%{_bindir}/clang-doc%{bin_suffix}
%{_bindir}/clang-extdef-mapping%{bin_suffix}
%{_bindir}/clang-move%{bin_suffix}
%{_bindir}/clang-offload-wrapper%{bin_suffix}
%{_bindir}/clang-scan-deps%{bin_suffix}
%{_bindir}/pp-trace%{bin_suffix}
%{_bindir}/clang-offload-bundler%{bin_suffix}
%{_bindir}/diagtool%{bin_suffix}
%{_bindir}/hmaptool%{bin_suffix}
%{_bindir}/c-index-test%{bin_suffix}
%{_emacs_sitestartdir}/clang-format.el
%{pkg_sharedir}/clang/clang-format.py*
%{pkg_sharedir}/clang/clang-format-diff.py*
%{pkg_bindir}

%files libs
%{pkg_libdir}/*.so.*
%{pkg_libdir}/clang/%{version}

%files devel
%{pkg_libdir}/*.so
%{pkg_includedir}/clang/
%{pkg_includedir}/clang-c/
%{pkg_libdir}/cmake/*
%dir %{pkg_sharedir}/clang/

%files resource-filesystem
%dir %{pkg_libdir}/clang/%{version}/
%dir %{pkg_libdir}/clang/%{version}/include/
%dir %{pkg_libdir}/clang/%{version}/lib/
%dir %{pkg_libdir}/clang/%{version}/share/

%files help
%{_mandir}/man1/*

%files analyzer
%{_bindir}/scan-view%{bin_suffix}
%{_bindir}/scan-build%{bin_suffix}
%{pkg_libexecdir}/ccc-analyzer
%{pkg_libexecdir}/c++-analyzer
%{pkg_sharedir}/scan-view
%{pkg_sharedir}/scan-build
%{_mandir}/man1/*

%files tools-extra
%{_bindir}/clangd%{bin_suffix}
%{_bindir}/clang-apply-replacements%{bin_suffix}
%{_bindir}/clang-change-namespace%{bin_suffix}
%{_bindir}/clang-include-fixer%{bin_suffix}
%{_bindir}/clang-query%{bin_suffix}
%{_bindir}/clang-refactor%{bin_suffix}
%{_bindir}/clang-reorder-fields%{bin_suffix}
%{_bindir}/clang-rename%{bin_suffix}
%{_bindir}/clang-tidy%{bin_suffix}
%{_bindir}/find-all-symbols%{bin_suffix}
%{_bindir}/modularize%{bin_suffix}
%{_emacs_sitestartdir}/clang-rename.el
%{_emacs_sitestartdir}/clang-include-fixer.el
%{pkg_sharedir}/clang/clang-include-fixer.py*
%{pkg_sharedir}/clang/clang-tidy-diff.py*
%{pkg_sharedir}/clang/run-clang-tidy.py*
%{pkg_sharedir}/clang/run-find-all-symbols.py*
%{pkg_sharedir}/clang/clang-rename.py*
%{pkg_sharedir}/clang/index.js
%{pkg_sharedir}/clang/clang-doc-default-stylesheet.css

%files -n git-clang-format
%{_bindir}/git-clang-format%{bin_suffix}

%changelog
* Tue Apr 18 2023 jchzhou <zhoujiacheng@iscas.ac.cn> - 12.0.1-4
- init for clang-12

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
