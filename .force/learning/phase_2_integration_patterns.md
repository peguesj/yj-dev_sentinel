# Key Technical Patterns - Phase 2 Integration

## Smart Component Bridge Pattern
Created `SmartJobMatchAnalysis` component that:
- Automatically detects data format (legacy Resume vs ParsedResume)
- Provides seamless fallback between enhanced and basic analysis
- Handles type conversion between different interface definitions
- Maintains backward compatibility while enabling new features

## Type Safety Strategy
Resolved conflicts between multiple type definition files by:
- Using explicit type conversion functions instead of `any` casting
- Creating adapter functions to bridge interface differences
- Adding missing properties (like `user_id`) for RLS compatibility
- Using `'property' in object` instead of `hasOwnProperty()`

## Supabase Web Project Patterns
Established correct CLI usage for web (non-Docker) projects:
- Use `--use-api` flag for Edge Function deployment
- Use `--linked` flag for database operations
- Environment variables need `VITE_` prefix for client access
- Maintain fallback values in client configuration

## Component Integration Approach
Updated main application by:
- Replacing basic analysis with smart wrapper component
- Updating import paths to match directory structure
- Removing unused dependencies and effects
- Maintaining existing prop interfaces where possible

## Vector Embedding Workflow
Implemented end-to-end semantic analysis:
- Edge Function generates embeddings via OpenAI API
- Database stores vectors with pgvector extension
- Frontend components consume semantic similarity scores
- Fallback to keyword analysis when vector data unavailable

## Error Handling Strategy
- Graceful degradation when enhanced features unavailable
- User-friendly error messages for configuration issues
- Development vs production environment considerations
- Type-safe error boundaries and validation

These patterns provide a foundation for future feature development while maintaining system stability and backward compatibility.
