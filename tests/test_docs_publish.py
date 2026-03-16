from bear_brain.docs_publish import classify_publish_target


def test_spec_goes_to_product_spec() -> None:
    target = classify_publish_target(doc_type="spec")
    assert target.as_posix().endswith("docs/product/SPEC.md")
