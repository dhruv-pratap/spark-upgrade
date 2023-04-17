#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#  #
#    http://www.apache.org/licenses/LICENSE-2.0
#  #
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#  KIND, either express or implied.  See the License for the
#  specific language governing permissions and limitations
#  under the License.
#

from pysparkler.pyspark_22_to_23 import (
    DataFrameReplaceWithoutUsingDictionary,
    PandasRespectSessionTimeZone,
    RequiredPandasVersionCommentWriter,
)
from tests.conftest import rewrite


def test_adds_required_pandas_version_comment_to_import_statements():
    given_code = """
import pandas
import pyspark
"""
    modified_code = rewrite(given_code, RequiredPandasVersionCommentWriter())
    expected_code = """
import pandas  # PY22-23-001: PySpark 2.3 requires pandas version 0.19.2 or higher
import pyspark
"""
    assert modified_code == expected_code


def test_adds_pandas_respects_session_timezone_comment_when_session_timezone_config_is_being_set():
    given_code = """
import pandas
import pyspark

spark.conf.set("spark.sql.session.timeZone", "America/Los_Angeles")
df = spark.createDataFrame([28801], "long").selectExpr("timestamp(value) as ts")
df.show()

df.toPandas()
"""
    modified_code = rewrite(given_code, PandasRespectSessionTimeZone())
    expected_code = """
import pandas
import pyspark

spark.conf.set("spark.sql.session.timeZone", "America/Los_Angeles")  # PY22-23-002: As of PySpark 2.3 the behavior of timestamp values for Pandas related functionalities was changed to respect session timezone. If you want to use the old behavior, you need to set a configuration spark.sql.execution.pandas.respectSessionTimeZone to False.
df = spark.createDataFrame([28801], "long").selectExpr("timestamp(value) as ts")
df.show()

df.toPandas()
"""
    assert modified_code == expected_code


def test_adds_comment_when_dataframe_replace_is_called_without_using_dictionary_with_no_values():
    given_code = """
import pyspark

df = spark.createDataFrame([
    (10, 80, "Alice"),
    (5, None, "Bob"),
    (None, 10, "Tom"),
    (None, None, None)],
    schema=["age", "height", "name"])

df.na.replace('Alice').show()
"""
    modified_code = rewrite(given_code, DataFrameReplaceWithoutUsingDictionary())
    expected_code = """
import pyspark

df = spark.createDataFrame([
    (10, 80, "Alice"),
    (5, None, "Bob"),
    (None, 10, "Tom"),
    (None, None, None)],
    schema=["age", "height", "name"])

df.na.replace('Alice').show()  # PY22-23-003: As of PySpark 2.3, df.replace does not allow to omit value when to_replace is not a dictionary. Previously, value could be omitted in the other cases and had None by default, which is counterintuitive and error-prone.
"""
    assert modified_code == expected_code


def test_does_not_add_comment_when_dataframe_replace_is_called_without_using_dictionary_but_with_values():
    given_code = """
import pyspark

df = spark.createDataFrame([
    (10, 80, "Alice"),
    (5, None, "Bob"),
    (None, 10, "Tom"),
    (None, None, None)],
    schema=["age", "height", "name"])

df.na.replace(['Alice', 'Bob'], ['A', 'B'], 'name').show()
"""
    modified_code = rewrite(given_code, DataFrameReplaceWithoutUsingDictionary())
    assert modified_code == given_code


def test_does_not_add_comment_when_dataframe_replace_is_called_using_dictionary_and_without_values():
    given_code = """
import pyspark

df = spark.createDataFrame([
    (10, 80, "Alice"),
    (5, None, "Bob"),
    (None, 10, "Tom"),
    (None, None, None)],
    schema=["age", "height", "name"])

df.na.replace({'Alice': 'A', 'Bob': 'B'}).show()
"""
    modified_code = rewrite(given_code, DataFrameReplaceWithoutUsingDictionary())
    assert modified_code == given_code