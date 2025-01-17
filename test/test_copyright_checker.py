from __future__ import annotations

import datetime

import pytest

from custom_hooks import copyright_checker


def test_no_args(capsys):
    with pytest.raises(SystemExit):
        copyright_checker.main()
    cap = capsys.readouterr()
    assert " error: the following arguments are required: -o/--owner" in cap.err


def test_no_copyright_py(capsys, tmpdir):
    f = tmpdir / "a.py"
    f.write("hello world")
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    year = str(datetime.date.today().year)
    assert f"#\n# Copyright (c) {year} by fake. All rights reserved.\n#\n\n" in out
    cap = capsys.readouterr()
    assert f"Adding copyright to {f}" in cap.out


def test_no_copyright_empty_py(capsys, tmpdir):
    f = tmpdir / "a.py"
    f.write("")
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    year = str(datetime.date.today().year)
    assert f"#\n# Copyright (c) {year} by fake. All rights reserved.\n#\n" in out
    cap = capsys.readouterr()
    assert f"Adding copyright to {f}" in cap.out


def test_current_copyright_py(capsys, tmpdir):
    f = tmpdir / "a.py"
    year = str(datetime.date.today().year)
    f.write(f"#\n# Copyright (c) {year} by fake. All rights reserved.\n#\n")
    assert copyright_checker.main(["-o", "fake", f"{f}"]) == 0


def test_old_copyright_py(capsys, tmpdir):
    f = tmpdir / "a.py"
    f.write("#\n# Copyright (c) 2000 by fake. All rights reserved.\n#\n")
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    year = str(datetime.date.today().year)
    assert f"#\n# Copyright (c) 2000, {year} by fake. All rights reserved.\n#\n" in out
    cap = capsys.readouterr()
    assert f"Updating copyright: {f}" in cap.out


def test_old_range_copyright_py(capsys, tmpdir):
    f = tmpdir / "a.py"
    f.write("#\n# Copyright (c) 2000, 2022 by fake. All rights reserved.\n#\n")
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    year = str(datetime.date.today().year)
    assert f"#\n# Copyright (c) 2000, {year} by fake. All rights reserved.\n#\n" in out
    cap = capsys.readouterr()
    assert f"Updating copyright: {f}" in cap.out


def test_multiple_old_copyright_py(capsys, tmpdir):
    f = tmpdir / "a.py"
    f.write(
        "#\n# Copyright (c) 2000 by fake. All rights reserved.\n"
        "#\nhello\n# Copyright (c) 2000 by fake. All rights reserved."
    )
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    year = str(datetime.date.today().year)
    assert (
        f"#\n# Copyright (c) 2000, {year} by fake. All rights reserved.\n"
        "#\nhello\n# Copyright (c) 2000 by fake. All rights reserved." in out
    )
    cap = capsys.readouterr()
    assert f"Updating copyright: {f}" in cap.out


def test_multiple_old_range_copyright_py(capsys, tmpdir):
    f = tmpdir / "a.py"
    f.write(
        "#\n# Copyright (c) 2000, 2022 by fake. All rights reserved.\n"
        "#\nhello\n# Copyright (c) 2000, 2022 by fake. All rights reserved."
    )
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    year = str(datetime.date.today().year)
    assert (
        f"#\n# Copyright (c) 2000, {year} by fake. All rights reserved.\n"
        "#\nhello\n# Copyright (c) 2000, 2022 by fake. All rights reserved." in out
    )
    cap = capsys.readouterr()
    assert f"Updating copyright: {f}" in cap.out


def test_multiple_one_new_one_old_copyright_py(capsys, tmpdir):
    year = str(datetime.date.today().year)
    f = tmpdir / "a.py"
    f.write(
        "#\n# Copyright (c) 2000, 2022 by fake. All rights reserved.\n"
        f"#\nhello\n# Copyright (c) {year} by fake. All rights reserved."
    )
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    assert (
        f"#\n# Copyright (c) 2000, {year} by fake. All rights reserved.\n"
        f"#\nhello\n# Copyright (c) {year} by fake. All rights reserved." in out
    )
    cap = capsys.readouterr()
    assert f"Updating copyright: {f}" in cap.out


def test_old_copyright_py_no_changes(tmpdir, fake_git_no_changes):
    f = tmpdir / "a.py"
    t = "#\n# Copyright (c) 2000 by fake. All rights reserved.\n#\n"
    f.write(t)
    assert copyright_checker.main(["-o", "fake", f"{f}"]) == 0
    out = f.read()
    assert t == out


def test_old_copyright_py_no_update(capsys, tmpdir):
    f = tmpdir / "a.py"
    t = "#\n# Copyright (c) 2000 by fake. All rights reserved.\n#\n"
    f.write(t)
    assert copyright_checker.main(["-o", "fake", "-n", f"{f}"]) == 1
    out = f.read()
    assert t == out
    cap = capsys.readouterr()
    assert f"Copyright is out-of-date: {f}" in cap.out


def test_no_copyright_py_with_shebang_and_encoding(capsys, tmpdir):
    f = tmpdir / "a.py"
    f.write("#! /usr/bin/env python3\n# coding: utf-8\n\nhello world")
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    year = str(datetime.date.today().year)
    assert (
        "#! /usr/bin/env python3\n# coding: utf-8\n#\n"
        f"# Copyright (c) {year} by fake. All rights reserved.\n#\n\nhello world" in out
    )
    cap = capsys.readouterr()
    assert f"Adding copyright to {f}" in cap.out


def test_no_copyright_py_with_encoding(capsys, tmpdir):
    f = tmpdir / "a.py"
    f.write("# -*- coding: iso-8859-15 -*-\n\nhello world")
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    year = str(datetime.date.today().year)
    assert (
        "# -*- coding: iso-8859-15 -*-\n#\n"
        f"# Copyright (c) {year} by fake. All rights reserved.\n#\n\nhello world" in out
    )
    cap = capsys.readouterr()
    assert f"Adding copyright to {f}" in cap.out


def test_no_copyright_sh_with_shebang(capsys, tmpdir):
    f = tmpdir / "a.sh"
    f.write("#! /usr/bin/env bash\n\nhello world")
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    year = str(datetime.date.today().year)
    assert (
        "#! /usr/bin/env bash\n#\n"
        f"# Copyright (c) {year} by fake. All rights reserved.\n#\n\nhello world" in out
    )
    cap = capsys.readouterr()
    assert f"Adding copyright to {f}" in cap.out


def test_no_copyright_md(capsys, tmpdir):
    f = tmpdir / "a.md"
    f.write("hello world")
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    year = str(datetime.date.today().year)
    assert (
        f"[//]: # (Copyright \\(c\\) {year} by fake. All rights reserved.)\n\n"
        "hello world" in out
    )
    cap = capsys.readouterr()
    assert f"Adding copyright to {f}" in cap.out


def test_old_copyright_md(capsys, tmpdir):
    f = tmpdir / "a.md"
    f.write(
        "[//]: # (Copyright \\(c\\) 2000 by fake. All rights reserved.)\n\nhello world"
    )
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    year = str(datetime.date.today().year)
    assert (
        f"[//]: # (Copyright \\(c\\) 2000, {year} by fake. All rights reserved.)"
        "\n\nhello world" in out
    )
    cap = capsys.readouterr()
    assert f"Updating copyright: {f}" in cap.out


def test_no_copyright_groovy(capsys, tmpdir):
    f = tmpdir / "a.groovy"
    f.write("hello world")
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    year = str(datetime.date.today().year)
    assert f"/*\n * Copyright (c) {year} by fake. All rights reserved.\n */\n\n" in out
    cap = capsys.readouterr()
    assert f"Adding copyright to {f}" in cap.out


def test_no_copyright_fake_ending(capsys, tmpdir):
    f = tmpdir / "a.fake"
    f.write("hello world")
    copyright_checker.main(["-o", "fake", f"{f}"])
    cap = capsys.readouterr()
    assert f"Missing copyright for file {f}" in cap.out


def test_curr_copyright_later_in_text(capsys, tmpdir):
    year = str(datetime.date.today().year)
    f = tmpdir / "a.py"
    f.write(
        '#\n#\ndef test():\n"This is a test"\n    return 1 + 1\n\n'
        f"# Copyright (c) {year} by fake. All rights reserved."
    )
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    assert (
        f"#\n# Copyright (c) {year} by fake. All rights reserved.\n#\n\n"
        '#\n#\ndef test():\n"This is a test"\n    return 1 + 1\n\n'
        f"# Copyright (c) {year} by fake. All rights reserved." in out
    )
    cap = capsys.readouterr()
    assert f"Adding copyright to {f}" in cap.out


def test_chained_licenses_in_java_current_copyright(capsys, tmpdir):
    f = tmpdir / "a.java"
    year = str(datetime.date.today().year)
    f.write(
        f"""
/*! ****************************************************************************
 *
 * Other company
 *
 * Copyright (C) 2002-2017 by other
 *
 *******************************************************************************
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 ******************************************************************************/

/**
 * Copyright (c) 2016, {year} by fake. All rights reserved.
 */
package something;

import java.io.something;
        """
    )
    assert copyright_checker.main(["-o", "fake", f"{f}"]) == 0


def test_chained_licenses_in_java_old_copyright(capsys, tmpdir):
    f = tmpdir / "a.java"
    year = str(datetime.date.today().year)
    f.write(
        """
/*! ****************************************************************************
 *
 * Other company
 *
 * Copyright (C) 2002-2017 by other
 *
 *******************************************************************************
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 ******************************************************************************/

/**
 * Copyright (c) 2016, 2021 by fake. All rights reserved.
 */
package something;

import java.io.something;
"""
    )
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    assert (
        f"""
/*! ****************************************************************************
 *
 * Other company
 *
 * Copyright (C) 2002-2017 by other
 *
 *******************************************************************************
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 ******************************************************************************/

/**
 * Copyright (c) 2016, {year} by fake. All rights reserved.
 */
package something;

import java.io.something;
"""
        in out
    )
    cap = capsys.readouterr()
    assert f"Updating copyright: {f}" in cap.out


def test_chained_licenses_in_java_old_copyright_andh_later(capsys, tmpdir):
    f = tmpdir / "a.java"
    year = str(datetime.date.today().year)
    f.write(
        """
/*! ****************************************************************************
 *
 * Other company
 *
 * Copyright (C) 2002-2017 by other
 *
 *******************************************************************************
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 ******************************************************************************/

/**
 * Copyright (c) 2016, 2021 by fake. All rights reserved.
 */
package something;

import java.io.something;
/**
 * Copyright (c) 2016, 2023 by fake. All rights reserved.
 */
"""
    )
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    assert (
        f"""
/*! ****************************************************************************
 *
 * Other company
 *
 * Copyright (C) 2002-2017 by other
 *
 *******************************************************************************
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 ******************************************************************************/

/**
 * Copyright (c) 2016, {year} by fake. All rights reserved.
 */
package something;

import java.io.something;
/**
 * Copyright (c) 2016, 2023 by fake. All rights reserved.
 */
"""
        in out
    )
    cap = capsys.readouterr()
    assert f"Updating copyright: {f}" in cap.out


def test_no_copyright_py_with_docstring(capsys, tmpdir):
    f = tmpdir / "a.py"
    f.write('"""\nSimple module"""hello world')
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    year = str(datetime.date.today().year)
    assert (
        f"# Copyright (c) {year} by fake. All rights reserved.\n#\n\n"
        '"""\nSimple module"""hello world' in out
    )
    cap = capsys.readouterr()
    assert f"Adding copyright to {f}" in cap.out


def test_no_copyright_empty_lua(capsys, tmpdir):
    f = tmpdir / "a.lua"
    f.write("")
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    year = str(datetime.date.today().year)
    assert f"--\n-- Copyright (c) {year} by fake. All rights reserved.\n--\n" in out
    cap = capsys.readouterr()
    assert f"Adding copyright to {f}" in cap.out


def test_no_copyright_dockerfile(capsys, tmpdir):
    f = tmpdir / "Dockerfile"
    f.write("FROM alpine:3")
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    year = str(datetime.date.today().year)
    assert (
        f"#\n# Copyright (c) {year} by fake. All rights reserved.\n#\n\n"
        "FROM alpine:3" in out
    )
    cap = capsys.readouterr()
    assert f"Adding copyright to {f}" in cap.out


def test_old_copyright_gitignore(capsys, tmpdir):
    f = tmpdir / ".gitignore"
    f.write("#\n# Copyright (c) 2000 by fake. All rights reserved.\n#\n\n\n*egg*\n")
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    year = str(datetime.date.today().year)
    assert (
        f"#\n# Copyright (c) 2000, {year} by fake. All rights reserved.\n#\n"
        "\n\n*egg*\n" in out
    )
    cap = capsys.readouterr()
    assert f"Updating copyright: {f}" in cap.out
