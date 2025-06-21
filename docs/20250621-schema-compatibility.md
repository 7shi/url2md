# Schema Compatibility and Dynamic Properties

## Overview

This document describes the considerations and constraints for schema design when working with different LLM APIs, with a focus on the dynamic property generation patterns used in url2md. Understanding these constraints is crucial for maintaining compatibility across different LLM providers while leveraging the power of Pydantic's dynamic schema generation.

## LLM API Schema Constraints

### Gemini API Restrictions

The Google Gemini API has specific limitations that affect schema design:

#### `additionalProperties` Parameter

**Issue**: Gemini API does not support the `additionalProperties` parameter in JSON schemas.

**Manifestation**: When Pydantic models use `extra='forbid'` configuration, the generated JSON schema includes `"additionalProperties": false`, which causes a `ValueError` in the Gemini API.

**Error Example**:
```
ValueError: additional_properties parameter is not supported in Gemini API.
```

**Solution**: Avoid using `extra='forbid'` or similar configurations that generate `additionalProperties` in the JSON schema.

#### Compatible Schema Patterns

```python
# ❌ Incompatible with Gemini API
class MyModel(BaseModel):
    field: str
    
    class Config:
        extra = 'forbid'  # Generates additionalProperties: false

# ❌ Also incompatible
MyDynamicModel = create_model(
    'MyDynamicModel',
    field=(str, Field(description="A field")),
    __config__=ConfigDict(extra='forbid')
)

# ✅ Compatible with Gemini API
class MyModel(BaseModel):
    field: str
    # No extra configuration

# ✅ Compatible dynamic model
MyDynamicModel = create_model(
    'MyDynamicModel',
    field=(str, Field(description="A field"))
    # No __config__ parameter
)
```

## Dynamic Schema Generation Patterns

### `create_model` for Runtime Schema Generation

Pydantic's `create_model` function enables dynamic schema generation based on runtime parameters, which is essential for use cases like translation where the field structure depends on input data.

#### Basic Pattern

```python
from pydantic import BaseModel, Field, create_model
from typing import List, Type

def create_dynamic_schema(field_names: List[str]) -> Type[BaseModel]:
    """
    Create a Pydantic schema with dynamic fields.
    
    Args:
        field_names: List of field names to include in the schema
        
    Returns:
        Pydantic BaseModel class with dynamic fields
    """
    # Build field definitions
    fields = {
        name: (str, Field(description=f"Value for {name}"))
        for name in field_names
    }
    
    # Create dynamic model - API compatible
    DynamicModel = create_model(
        'DynamicModel',
        **fields
        # No __config__ to ensure API compatibility
    )
    
    return DynamicModel
```

#### Nested Dynamic Schemas

For more complex structures involving nested dynamic models:

```python
def create_nested_dynamic_schema(terms: List[str]) -> Type[BaseModel]:
    """
    Create nested dynamic schema compatible with LLM APIs.
    """
    # Dynamic fields for inner model
    translation_fields = {
        term: (str, Field(description=f"Translation of '{term}'"))
        for term in terms
    }
    
    # Create inner dynamic model
    TranslationDict = create_model(
        'TranslationDict',
        **translation_fields
        # No configuration constraints
    )
    
    # Outer model with nested dynamic structure
    class Result(BaseModel):
        translations: TranslationDict
        metadata: dict = Field(default_factory=dict)
    
    return Result
```

## API Compatibility Best Practices

### 1. Schema Validation Strategy

**Principle**: Rely on Pydantic's built-in validation rather than schema-level constraints.

```python
# ✅ Good: Use Pydantic validation
class MyModel(BaseModel):
    required_field: str
    optional_field: Optional[str] = None
    
    @validator('required_field')
    def validate_required_field(cls, v):
        if not v.strip():
            raise ValueError('Field cannot be empty')
        return v

# ❌ Avoid: Schema-level constraints that may not be supported
class MyModel(BaseModel):
    required_field: str
    
    class Config:
        extra = 'forbid'  # May cause API compatibility issues
```

### 2. Field Definition Patterns

**Required Fields**: Use type annotations without default values.
**Optional Fields**: Use `Optional[Type]` with default values.
**Dynamic Descriptions**: Generate descriptions programmatically for multi-language support.

```python
def create_language_aware_schema(language: Optional[str] = None) -> Type[BaseModel]:
    """Create schema with language-aware field descriptions."""
    lang_suffix = f" in {language}" if language else ""
    
    class LanguageAwareModel(BaseModel):
        title: str = Field(
            description=f"Title of the content{lang_suffix}"
        )
        summary: str = Field(
            description=f"Summary of the content{lang_suffix}"
        )
        tags: List[str] = Field(
            description=f"List of relevant tags{lang_suffix}"
        )
    
    return LanguageAwareModel
```

### 3. API Testing Strategy

**Validation Approach**: Test schema compatibility before deployment.

```python
def test_api_compatibility(schema_class: Type[BaseModel]):
    """
    Test schema compatibility with target LLM API.
    """
    try:
        # Generate JSON schema
        json_schema = schema_class.model_json_schema()
        
        # Check for problematic properties
        problematic_keys = ['additionalProperties']
        
        def check_schema(schema_dict: dict, path: str = ""):
            for key, value in schema_dict.items():
                current_path = f"{path}.{key}" if path else key
                
                if key in problematic_keys:
                    print(f"⚠️  Found {key} at {current_path}")
                
                if isinstance(value, dict):
                    check_schema(value, current_path)
        
        check_schema(json_schema)
        print("✅ Schema appears compatible")
        
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
```

## Case Study: Translation Schema Evolution

### Problem

The original translation schema used `extra='forbid'` to ensure strict validation:

```python
# Original implementation (problematic)
TranslationDict = create_model(
    'TranslationDict',
    **translation_fields,
    __config__=ConfigDict(extra='forbid')  # Caused Gemini API error
)

class TranslateResult(BaseModel):
    translations: TranslationDict
    
    class Config:
        extra = 'forbid'  # Also problematic
```

### Solution

Removed configuration constraints while maintaining functionality:

```python
# Fixed implementation (API compatible)
TranslationDict = create_model(
    'TranslationDict',
    **translation_fields
    # No __config__ parameter
)

class TranslateResult(BaseModel):
    translations: TranslationDict
    # No Config class
```

### Impact

- ✅ **Compatibility**: Resolved Gemini API errors
- ✅ **Functionality**: Maintained full translation capabilities
- ✅ **Type Safety**: Preserved Pydantic validation benefits
- ✅ **Performance**: No degradation in validation speed

## Multi-API Compatibility

### Design Principles

1. **Lowest Common Denominator**: Design schemas that work across multiple LLM APIs
2. **Feature Detection**: Test API capabilities rather than making assumptions
3. **Graceful Degradation**: Provide fallbacks for unsupported features
4. **Documentation**: Clearly document API-specific constraints

### Provider-Specific Considerations

#### Google Gemini API
- ❌ No `additionalProperties` support
- ✅ Supports nested schemas
- ✅ Supports dynamic field generation
- ✅ Supports complex validation rules

#### OpenAI API (Future Compatibility)
- ✅ Generally more permissive with JSON schema features
- ✅ Supports `additionalProperties`
- ✅ Supports advanced schema features

#### Anthropic Claude API (Future Compatibility)
- ℹ️ Schema support varies by implementation
- ℹ️ May have different constraint patterns

## Testing and Validation

### Development Workflow

1. **Schema Design**: Create Pydantic models with API compatibility in mind
2. **Local Testing**: Validate schema generation and structure
3. **API Testing**: Test with actual LLM API calls
4. **Integration Testing**: Verify end-to-end functionality
5. **Documentation**: Update compatibility notes

### Automated Testing

```python
def test_schema_api_compatibility():
    """Test suite for schema API compatibility."""
    
    # Test dynamic schema generation
    terms = ['hello', 'world', 'test']
    schema_class = create_translate_schema_class(terms)
    
    # Verify schema can be created
    assert schema_class is not None
    
    # Test JSON schema generation
    json_schema = schema_class.model_json_schema()
    assert 'properties' in json_schema
    
    # Check for API-incompatible features
    schema_str = str(json_schema)
    assert 'additionalProperties' not in schema_str
    
    # Test with llm7shi integration
    from llm7shi import config_from_schema
    config = config_from_schema(schema_class)
    assert config is not None
```

## Future Considerations

### Evolving API Landscape

As LLM APIs evolve, schema compatibility requirements may change:

- **New Features**: APIs may add support for previously unsupported features
- **Deprecations**: Existing features may be deprecated or removed
- **Standards**: Industry standards for LLM schema definitions may emerge

### Monitoring Strategy

1. **Version Tracking**: Monitor API version changes and feature updates
2. **Compatibility Testing**: Regular testing against multiple API versions
3. **Community Feedback**: Monitor community reports of compatibility issues
4. **Documentation Updates**: Keep compatibility documentation current

### Migration Planning

When API constraints change:

1. **Impact Assessment**: Evaluate how changes affect existing schemas
2. **Backward Compatibility**: Ensure existing implementations continue working
3. **Migration Path**: Provide clear upgrade paths for new features
4. **Testing**: Comprehensive testing across API versions

## Conclusion

Schema compatibility with LLM APIs requires careful consideration of provider-specific constraints while maintaining the benefits of type-safe, dynamic schema generation. By following the patterns and principles outlined in this document, developers can create robust, compatible schemas that work across different LLM providers while leveraging the full power of Pydantic's validation and type safety features.

The key is to design schemas that are flexible and compatible by default, adding provider-specific optimizations only when necessary and well-tested. This approach ensures maximum compatibility and future-proofing as the LLM API landscape continues to evolve.