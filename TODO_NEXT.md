# TODO_NEXT.md

## Codebase Improvement - Remaining Tasks

### High Priority

1. **Complete OACP Modules**
   - [ ] Create `oacp/protocol.py` - Protocol specifications
   - [ ] Create `oacp/runtime.py` - Runtime attestation
   - [ ] Create `oacp/attestation.py` - Attestation evidence
   - [ ] Uncomment imports in `oacp/__init__.py` once modules exist

2. **Documentation Files**
   - [ ] Create `README.md` with installation and usage instructions
   - [ ] Create `CHANGELOG.md` with version history
   - [ ] Create `docs/` directory with proper documentation

3. **deploy_guardian.py Improvements**
   - [ ] Add type hints to all methods
   - [ ] Add docstrings to remaining functions
   - [ ] Reduce cyclomatic complexity in main()
   - [ ] Add unit tests for guardian checks
   - [ ] Add integration tests

### Medium Priority

4. **Additional Test Coverage**
   - [ ] Add integration tests for end-to-end flows
   - [ ] Add performance tests for database operations
   - [ ] Add concurrency tests for message bus
   - [ ] Test database migration paths

5. **Code Quality Tools**
   - [ ] Run `ruff check .` and fix all issues
   - [ ] Run `mypy .` and fix type errors
   - [ ] Run `bandit -r .` for security audit
   - [ ] Set up pre-commit hooks

6. **CI/CD Setup**
   - [ ] Create `.github/workflows/ci.yml`
   - [ ] Add automated testing on push
   - [ ] Add code coverage reporting
   - [ ] Add automated security scanning

### Low Priority

7. **Additional Features**
   - [ ] Add message encryption support
   - [ ] Add message persistence across reboots
   - [ ] Add message expiration/TTL
   - [ ] Add message search functionality
   - [ ] Add metrics and monitoring

8. **Documentation**
   - [ ] API documentation with Sphinx
   - [ ] Usage examples directory
   - [ ] Architecture decision records (ADRs)
   - [ ] Contributing guidelines

9. **Refactoring**
   - [ ] Extract SQL queries to constants
   - [ ] Create abstract base class for storage backends
   - [ ] Add async support for I/O operations
   - [ ] Consider ORM (SQLAlchemy) for complex queries

### Technical Debt

10. **Known Issues to Address**
    - [ ] deploy_guardian.py has complex nested conditionals
    - [ ] Some methods in chaiwala.py are long (>50 lines)
    - [ ] Test coverage for error conditions could be improved
    - [ ] No database migration strategy defined

### Blockers

- None currently

### Dependencies

- All dependencies documented in requirements.txt
- Security scanning tools (safety, bandit) added but not yet run

---

*Generated: 2026-02-12*
