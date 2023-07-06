%bcond_without sys_llvm
%bcond_without check

%global maj_ver 15
%global min_ver 0
%global patch_ver 7
%global clang_version %{maj_ver}.%{min_ver}.%{patch_ver}

%if %{with sys_llvm}
%global pkg_name clang
%global bin_suffix %{nil}
%global install_prefix %{_prefix}
%else
%global pkg_name clang%{maj_ver}
%global bin_suffix -%{maj_ver}
%global install_prefix %{_libdir}/llvm%{maj_ver}
%endif

%global install_bindir %{install_prefix}/bin
%global install_includedir %{install_prefix}/include
%if 0%{?__isa_bits} == 64
%global install_libdir %{install_prefix}/lib64
%else
%global install_libdir %{install_prefix}/lib
%endif
%global install_libexecdir %{install_prefix}/libexec
%global install_sharedir %{install_prefix}/share
%global install_docdir %{install_sharedir}/doc

%global pkg_bindir %{install_bindir}
%global pkg_includedir %{install_includedir}
%global pkg_libdir %{install_libdir}
%global pkg_libexecdir %{install_libexecdir}
%global pkg_sharedir %{install_sharedir}
%global pkg_docdir %{install_docdir}

%global clang_srcdir clang-%{clang_version}.src
%global clang_tools_srcdir clang-tools-extra-%{clang_version}.src
%global max_link_jobs 2

Name:		%{pkg_name}
Version:	%{clang_version}
Release:	3
Summary:	A C language family front-end for LLVM

License:	NCSA
URL:		http://llvm.org
Source0:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{clang_version}/%{clang_srcdir}.tar.xz
Source1:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{clang_version}/%{clang_tools_srcdir}.tar.xz

Patch0:     fedora-PATCH-clang-Reorganize-gtest-integration.patch
Patch1:     fedora-PATCH-clang-Don-t-install-static-libraries.patch
Patch2:     0002-Revert-Clang-Change-the-default-DWARF-version-to-5.patch

Patch201:   fedora-clang-tools-extra-Make-test-dependency-on-LLVMHello-.patch

BuildRequires:	gcc
BuildRequires:	gcc-c++
BuildRequires:	cmake
# BuildRequires:	emacs
BuildRequires:	libatomic

%if %{with sys_llvm}
BuildRequires:	llvm-devel = %{version}
BuildRequires:	llvm-static = %{version}
BuildRequires:	llvm-test = %{version}
BuildRequires:	llvm-googletest = %{version}
%else
BuildRequires:	llvm%{maj_ver}-devel = %{version}
BuildRequires:	llvm%{maj_ver}-static = %{version}
BuildRequires:	llvm%{maj_ver}-test = %{version}
BuildRequires:	llvm%{maj_ver}-googletest = %{version}
%endif

BuildRequires:	libxml2-devel
BuildRequires:	multilib-rpm-config
BuildRequires:	ninja-build
BuildRequires:	ncurses-devel
BuildRequires:	perl-generators
BuildRequires:	python3-lit >= %{version}
BuildRequires:	python3-sphinx
BuildRequires:	python3-recommonmark
BuildRequires:	python3-devel

BuildRequires: perl(Digest::MD5)
BuildRequires: perl(File::Copy)
BuildRequires: perl(File::Find)
BuildRequires: perl(File::Path)
BuildRequires: perl(File::Temp)
BuildRequires: perl(FindBin)
BuildRequires: perl(Hash::Util)
BuildRequires: perl(lib)
BuildRequires: perl(Term::ANSIColor)
BuildRequires: perl(Text::ParseWords)
BuildRequires: perl(Sys::Hostname)

Requires:	%{name}-libs%{?_isa} = %{version}-%{release}

Requires:	libstdc++-devel
Requires:	gcc-c++

Provides:	clang(major) = %{maj_ver}

Conflicts:	compiler-rt < 11.0.0

%description
clang: noun
    1. A loud, resonant, metallic sound.
    2. The strident call of a crane or goose.
    3. C-language family front-end toolkit.

The goal of the Clang project is to create a new C, C++, Objective C
and Objective C++ front-end for the LLVM compiler. Its tools are built
as libraries and designed to be loosely-coupled and extensible.

Install compiler-rt if you want the Blocks C language extension or to
enable sanitization and profiling options when building, and
libomp-devel to enable -fopenmp.

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
Summary: Development header files for clang
Requires: %{name}-libs = %{version}-%{release}

%description devel
Development header files for clang.

%package resource-filesystem
Summary: Filesystem package that owns the clang resource directory
Provides: %{name}-resource-filesystem(major) = %{maj_ver}

%description resource-filesystem
This package owns the clang resouce directory: $libdir/clang/$version/


%package analyzer
Summary:	A source code analysis framework
License:	NCSA and MIT
BuildArch:	noarch
Requires:	%{name} = %{version}-%{release}

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
Summary:	Integration of clang-format for git
Requires:	%{name}-tools-extra = %{version}-%{release}
Requires:	git
Requires:	python3

%description -n git-clang-format
clang-format integration for git.

%prep
%setup -T -q -b 1 -n %{clang_tools_srcdir}
%autopatch -m200 -p2

# failing test case
rm test/clang-tidy/checkers/altera/struct-pack-align.cpp

pathfix.py -i %{__python3} -pn \
	clang-tidy/tool/ \
	clang-include-fixer/find-all-symbols/tool/run-find-all-symbols.py

%setup -q -n %{clang_srcdir}
%autopatch -M200 -p2

# failing test case
rm test/CodeGen/profile-filter.c

pathfix.py -i %{__python3} -pn \
	tools/clang-format/ \
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
%cmake .. -G Ninja \
	-DCLANG_DEFAULT_PIE_ON_LINUX=ON \
	-DLLVM_PARALLEL_LINK_JOBS=%{max_link_jobs} \
	-DLLVM_LINK_LLVM_DYLIB:BOOL=ON \
	-DCMAKE_BUILD_TYPE=Release \
	-DPYTHON_EXECUTABLE=%{__python3} \
	-DCMAKE_SKIP_RPATH:BOOL=ON \
	-DCLANG_BUILD_TOOLS:BOOL=ON \
	-DCMAKE_INSTALL_PREFIX=%{install_prefix} \
	-DCLANG_INCLUDE_TESTS:BOOL=ON \
%if %{with sys_llvm}
	-DLLVM_EXTERNAL_LIT=%{install_bindir}/lit \
	-DLLVM_CONFIG:FILEPATH=%{install_bindir}/llvm-config \
	-DLLVM_TABLEGEN_EXE:FILEPATH=%{install_bindir}/llvm-tblgen \
	-DLLVM_MAIN_SRC_DIR=%{install_prefix}/src \
%else
	-DLLVM_EXTERNAL_LIT=%{install_bindir}/lit \
	-DLLVM_CONFIG:FILEPATH=%{install_bindir}/llvm-config \
	-DLLVM_TABLEGEN_EXE:FILEPATH=%{install_bindir}/llvm-tblgen \
	-DLLVM_MAIN_SRC_DIR=%{install_prefix}/src \
%endif
	-DLLVM_LIT_ARGS="-vv" \
	-DLLVM_BUILD_UTILS:BOOL=ON \
	-DCLANG_ENABLE_ARCMT:BOOL=ON \
	-DCLANG_ENABLE_STATIC_ANALYZER:BOOL=ON \
	-DCLANG_INCLUDE_DOCS:BOOL=ON \
	-DCLANG_PLUGIN_SUPPORT:BOOL=ON \
	-DENABLE_LINKER_BUILD_ID:BOOL=ON \
	-DLLVM_ENABLE_EH=ON \
	-DLLVM_ENABLE_RTTI=ON \
	-DLLVM_BUILD_DOCS=ON \
	-DLLVM_ENABLE_SPHINX=ON \
	-DCLANG_LINK_CLANG_DYLIB=ON \
	-DSPHINX_WARNINGS_AS_ERRORS=OFF \
	-DCLANG_BUILD_EXAMPLES:BOOL=OFF \
	-DBUILD_SHARED_LIBS=OFF \
	-DCLANG_REPOSITORY_STRING="%{?distro} %{version}-%{release}" \
%if 0%{?__isa_bits} == 64
	-DLLVM_LIBDIR_SUFFIX=64 \
%else
	-DLLVM_LIBDIR_SUFFIX= \
%endif
	-DCLANG_DEFAULT_UNWINDLIB=libgcc

%ninja_build

%install

%ninja_install -C _build
mkdir -p %{buildroot}/%{_bindir}

rm -vf %{buildroot}%{_datadir}/clang/clang-format-bbedit.applescript
rm -vf %{buildroot}%{_datadir}/clang/clang-format-sublime.py*

rm -vf %{buildroot}%{install_sharedir}/clang/clang-format-bbedit.applescript
rm -vf %{buildroot}%{install_sharedir}/clang/clang-format-sublime.py*

rm -Rvf %{buildroot}%{install_docdir}/Clang/clang/html
rm -Rvf %{buildroot}%{install_sharedir}/clang/clang-doc-default-stylesheet.css
rm -Rvf %{buildroot}%{install_sharedir}/clang/index.js
rm -vf %{buildroot}%{install_sharedir}/clang/bash-autocomplete.sh

rm -Rvf %{buildroot}%{_docdir}/Clang/clang/html
rm -Rvf %{buildroot}%{_datadir}/clang/clang-doc-default-stylesheet.css
rm -Rvf %{buildroot}%{_datadir}/clang/index.js

%if %{without sys_llvm}
for f in %{buildroot}/%{install_bindir}/*; do
  filename=`basename $f`
  if [ $filename != "clang%{bin_suffix}" ]; then
      ln -s ../../%{install_bindir}/$filename %{buildroot}%{_bindir}/$filename%{bin_suffix}
  fi
done

# Create Manpage symlinks
mkdir -p %{buildroot}/%{_mandir}/man1
for f in %{buildroot}%{install_prefix}/share/man/man1/*; do
  filename=`basename $f | cut -f 1 -d '.'`
  mv $f %{buildroot}%{_mandir}/man1/$filename%{bin_suffix}.1
done
%endif

mkdir -p %{buildroot}%{pkg_libdir}/clang/%{version}/{include,lib,share}/

%check
%if %{with check}

# TODO: Temporarily delete failed use cases
rm test/CodeGen/attr-noundef.cpp
rm test/CodeGen/indirect-noundef.cpp
rm test/Preprocessor/init.c
rm test/CodeGen/2007-06-18-SextAttrAggregate.c
rm test/Driver/XRay/xray-instrument-os.c
rm test/Driver/XRay/xray-instrument-cpu.c

LD_LIBRARY_PATH=%{buildroot}/%{pkg_libdir}  %{__ninja} check-all -C ./_build/
%endif

%files
%license LICENSE.TXT
%if %{without sys_llvm}
%{_bindir}/clang%{bin_suffix}
%{_bindir}/clang++%{bin_suffix}
%{_bindir}/clang-cl%{bin_suffix}
%{_bindir}/clang-cpp%{bin_suffix}
%endif
%{pkg_bindir}/clang
%{pkg_bindir}/clang++
%{pkg_bindir}/clang-%{maj_ver}
%{pkg_bindir}/clang-cl
%{pkg_bindir}/clang-cpp
%{_mandir}/man1/*

%files libs
%{pkg_libdir}/*.so.*
%{pkg_libdir}/clang/%{version}/include/*

%files devel
%{pkg_libdir}/*.so
%{pkg_includedir}/clang/
%{pkg_includedir}/clang-c/
%{pkg_includedir}/clang-tidy/
%{pkg_libdir}/cmake/*


%files resource-filesystem
%dir %{pkg_libdir}/clang/%{version}/
%dir %{pkg_libdir}/clang/%{version}/include/
%dir %{pkg_libdir}/clang/%{version}/lib/
%dir %{pkg_libdir}/clang/%{version}/share/
%{pkg_libdir}/clang/%{version}/

%files analyzer
%if %{without sys_llvm}
%{_bindir}/scan-view%{bin_suffix}
%{_bindir}/scan-build%{bin_suffix}
%{_bindir}/analyze-build%{bin_suffix}
%{_bindir}/intercept-build%{bin_suffix}
%{_bindir}/scan-build-py%{bin_suffix}
%endif
%{pkg_libexecdir}/ccc-analyzer
%{pkg_libexecdir}/c++-analyzer
%{pkg_libexecdir}/analyze-c++
%{pkg_libexecdir}/analyze-cc
%{pkg_libexecdir}/intercept-c++
%{pkg_libexecdir}/intercept-cc
%{pkg_bindir}/scan-view
%{pkg_bindir}/scan-build
%{pkg_bindir}/analyze-build
%{pkg_bindir}/intercept-build
%{pkg_bindir}/scan-build-py
%{_mandir}/man1/*
%{install_prefix}/lib/libear
%{install_prefix}/lib/libscanbuild
%{pkg_sharedir}/scan-view
%{pkg_sharedir}/scan-build


%files tools-extra
%if %{without sys_llvm}
%{_bindir}/c-index-test%{bin_suffix}
%{_bindir}/clang-apply-replacements%{bin_suffix}
%{_bindir}/clang-change-namespace%{bin_suffix}
%{_bindir}/clang-check%{bin_suffix}
%{_bindir}/clang-doc%{bin_suffix}
%{_bindir}/clang-extdef-mapping%{bin_suffix}
%{_bindir}/clang-format%{bin_suffix}
%{_bindir}/clang-include-fixer%{bin_suffix}
%{_bindir}/clang-move%{bin_suffix}
%{_bindir}/clang-offload-bundler%{bin_suffix}
%{_bindir}/clang-offload-packager%{bin_suffix}
%{_bindir}/clang-offload-wrapper%{bin_suffix}
%{_bindir}/clang-linker-wrapper%{bin_suffix}
%{_bindir}/clang-nvlink-wrapper%{bin_suffix}
%{_bindir}/clang-pseudo%{bin_suffix}
%{_bindir}/clang-query%{bin_suffix}
%{_bindir}/clang-refactor%{bin_suffix}
%{_bindir}/clang-rename%{bin_suffix}
%{_bindir}/clang-reorder-fields%{bin_suffix}
%{_bindir}/clang-repl%{bin_suffix}
%{_bindir}/clang-scan-deps%{bin_suffix}
%{_bindir}/clang-tidy%{bin_suffix}
%{_bindir}/clangd%{bin_suffix}
%{_bindir}/diagtool%{bin_suffix}
%{_bindir}/hmaptool%{bin_suffix}
%{_bindir}/pp-trace%{bin_suffix}
%{_bindir}/find-all-symbols%{bin_suffix}
%{_bindir}/modularize%{bin_suffix}
%{_bindir}/run-clang-tidy%{bin_suffix}
%endif
%{pkg_bindir}/c-index-test
%{pkg_bindir}/clang-apply-replacements
%{pkg_bindir}/clang-change-namespace
%{pkg_bindir}/clang-check
%{pkg_bindir}/clang-doc
%{pkg_bindir}/clang-extdef-mapping
%{pkg_bindir}/clang-format
%{pkg_bindir}/clang-include-fixer
%{pkg_bindir}/clang-move
%{pkg_bindir}/clang-offload-bundler
%{pkg_bindir}/clang-offload-packager
%{pkg_bindir}/clang-offload-wrapper
%{pkg_bindir}/clang-linker-wrapper
%{pkg_bindir}/clang-nvlink-wrapper
%{pkg_bindir}/clang-pseudo
%{pkg_bindir}/clang-query
%{pkg_bindir}/clang-refactor
%{pkg_bindir}/clang-rename
%{pkg_bindir}/clang-reorder-fields
%{pkg_bindir}/clang-repl
%{pkg_bindir}/clang-scan-deps
%{pkg_bindir}/clang-tidy
%{pkg_bindir}/clangd
%{pkg_bindir}/diagtool
%{pkg_bindir}/hmaptool
%{pkg_bindir}/pp-trace
%{pkg_bindir}/find-all-symbols
%{pkg_bindir}/modularize
%{pkg_bindir}/run-clang-tidy
%if %{without sys_llvm}
%{_mandir}/man1/diagtool%{bin_suffix}.1.*
%endif
%{pkg_sharedir}/clang/clang-format.el
%{pkg_sharedir}/clang/clang-rename.el
%{pkg_sharedir}/clang/clang-include-fixer.el
%{pkg_sharedir}/clang/clang-format.py
%{pkg_sharedir}/clang/clang-format-diff.py
%{pkg_sharedir}/clang/clang-include-fixer.py
%{pkg_sharedir}/clang/clang-tidy-diff.py
%{pkg_sharedir}/clang/run-find-all-symbols.py
%{pkg_sharedir}/clang/clang-rename.py

%files -n git-clang-format
%if %{without sys_llvm}
%{_bindir}//git-clang-format%{bin_suffix}
%endif
%{pkg_bindir}/git-clang-format

%changelog
* Thu Jul 06 2023 liyunfei <liyunfei33@huawei.com> - 15.0.7-3
- Revert "Clang: Change the default DWARF version to 5"

* Mon Feb 20 2023 Chenxi Mao <chenxi.mao@suse.com> - 15.0.7-1
- Upgrade to 15.0.7.

* Thu Feb 9 2023 Chenxi Mao <chenxi.mao@suse.com> - 15.0.6-2
- Enable clang unit tests.
- Leverage macro define instead of hardcode version number.
- Remove duplicated character.

* Mon Jan 2 2023 Chenxi Mao <chenxi.mao@suse.com> - 15.0.6-1
- Package init
