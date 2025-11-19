# GitHub Issues Roadmap

**Last Updated**: 2025-01-18  
**Status**: Planning Document (Pre-Open Source)

---

## Purpose

This document is a **planning reference** for maintainers to create GitHub issues after open-sourcing. It outlines potential issues, priorities, and acceptance criteria.

**Note:** Once issues are created in GitHub, this document serves as a historical reference. Active work should be tracked via GitHub Issues, not this document.

---

## Overview

This document outlines potential GitHub issues to create after open-sourcing Sakura Sumi. These issues will demonstrate active development, provide clear contribution opportunities, and show a roadmap for future enhancements.

---

## Suggested GitHub Issues

### High Priority (Good for First-Time Contributors)

#### Issue #1: Add UI Screenshots to README
**Labels**: `documentation`, `good first issue`, `enhancement`  
**Priority**: Medium  
**Estimated Effort**: 1-2 hours

**Description:**
Add screenshots of the web portal to the README to help users understand what the interface looks like before installing.

**Tasks:**
- [ ] Capture screenshots of main web portal interface
- [ ] Capture screenshots of token estimation panel
- [ ] Capture screenshots of job history table
- [ ] Capture screenshots of results view
- [ ] Add screenshots to README with appropriate alt text
- [ ] Ensure screenshots are optimized for web (compressed, appropriate size)

**Acceptance Criteria:**
- README includes at least 3-4 screenshots showing key features
- Screenshots are clear and professional
- Images are optimized (<500KB each)
- Alt text provided for accessibility

---

#### Issue #2: Improve Test Coverage to 90%
**Labels**: `testing`, `good first issue`, `enhancement`  
**Priority**: Medium  
**Estimated Effort**: 4-8 hours

**Description:**
Current test coverage is 81%. Increase to 90% by adding tests for edge cases and uncovered code paths.

**Tasks:**
- [ ] Identify uncovered code paths using coverage report
- [ ] Add unit tests for edge cases in `pdf_converter.py`
- [ ] Add integration tests for error recovery scenarios
- [ ] Add tests for telemetry logging edge cases
- [ ] Add tests for web app error handling
- [ ] Verify coverage reaches 90%

**Acceptance Criteria:**
- Test coverage is ≥90%
- All new tests pass
- Coverage report shows improvement in previously uncovered areas

---

#### Issue #3: Add Docker Support
**Labels**: `enhancement`, `docker`, `devops`  
**Priority**: Medium  
**Estimated Effort**: 2-4 hours

**Description:**
Create Dockerfile and docker-compose.yml to make installation and deployment easier.

**Tasks:**
- [ ] Create Dockerfile with Python base image
- [ ] Create docker-compose.yml for web portal
- [ ] Add volume mounts for input/output directories
- [ ] Document Docker usage in README
- [ ] Test Docker build and run

**Acceptance Criteria:**
- Dockerfile builds successfully
- docker-compose.yml runs web portal
- Documentation includes Docker instructions
- Example docker-compose command works

---

### Medium Priority (Feature Enhancements)

#### Issue #4: Parallel PDF Generation for Smart Concatenation
**Labels**: `enhancement`, `performance`, `feature`  
**Priority**: Medium  
**Estimated Effort**: 6-10 hours

**Description:**
Currently, smart concatenation generates PDFs sequentially. Implement parallel generation to speed up processing for large codebases.

**Tasks:**
- [ ] Analyze current PDF generation flow
- [ ] Implement parallel PDF generation using ThreadPoolExecutor
- [ ] Add progress tracking for parallel operations
- [ ] Handle errors gracefully in parallel context
- [ ] Add tests for parallel generation
- [ ] Update documentation

**Acceptance Criteria:**
- PDFs generate in parallel when using smart concatenation
- Progress tracking works correctly
- Error handling maintains data integrity
- Tests pass for parallel generation
- Performance improvement measurable

---

#### Issue #5: CI/CD Pipeline Setup
**Labels**: `devops`, `enhancement`, `testing`  
**Priority**: Medium  
**Estimated Effort**: 4-6 hours

**Description:**
Set up GitHub Actions for automated testing, linting, and release management.

**Tasks:**
- [ ] Create GitHub Actions workflow for tests
- [ ] Add linting workflow (flake8/black)
- [ ] Add coverage reporting workflow
- [ ] Create release workflow for version tags
- [ ] Add status badges to README

**Acceptance Criteria:**
- Tests run automatically on PRs
- Linting runs automatically
- Coverage reports generated
- Release workflow works
- README shows build status badges

---

#### Issue #6: Enhanced Error Messages
**Labels**: `enhancement`, `ux`, `documentation`  
**Priority**: Low  
**Estimated Effort**: 2-4 hours

**Description:**
Improve error messages throughout the codebase to be more user-friendly and actionable.

**Tasks:**
- [ ] Audit current error messages
- [ ] Rewrite error messages to be clearer
- [ ] Add suggestions for common errors
- [ ] Link to relevant documentation
- [ ] Update tests for new error messages

**Acceptance Criteria:**
- Error messages are clear and actionable
- Common errors include suggested fixes
- Documentation links where appropriate
- Tests updated to match new messages

---

### Low Priority (Nice-to-Have Features)

#### Issue #7: Additional Visualization Types
**Labels**: `enhancement`, `feature`, `visualization`  
**Priority**: Low  
**Estimated Effort**: 4-6 hours

**Description:**
Add more chart types to the metrics visualization system (e.g., file type distribution, compression ratio over time).

**Tasks:**
- [ ] Design new chart types
- [ ] Implement file type distribution chart
- [ ] Implement compression ratio timeline (if applicable)
- [ ] Add chart configuration options
- [ ] Update documentation

**Acceptance Criteria:**
- New chart types render correctly
- Charts are visually appealing
- Configuration options work
- Documentation updated

---

#### Issue #8: Custom Key Folders for Smart Concatenation
**Labels**: `enhancement`, `feature`, `configuration`  
**Priority**: Low  
**Estimated Effort**: 3-5 hours

**Description:**
Allow users to specify custom "key folders" for smart concatenation priority, not just the default list.

**Tasks:**
- [ ] Add configuration option for key folders
- [ ] Update SmartConcatenationEngine to accept custom folders
- [ ] Add CLI/web UI options for key folders
- [ ] Update documentation
- [ ] Add tests

**Acceptance Criteria:**
- Users can specify custom key folders
- Custom folders get priority in grouping
- Configuration persists across runs
- Tests pass
- Documentation updated

---

#### Issue #9: ML-Based Directory Importance Scoring
**Labels**: `enhancement`, `feature`, `ml`, `advanced`  
**Priority**: Low  
**Estimated Effort**: 10-15 hours

**Description:**
Use machine learning to score directory importance for smarter grouping in smart concatenation.

**Tasks:**
- [ ] Research ML approaches for directory scoring
- [ ] Collect training data (directory structures)
- [ ] Implement scoring model
- [ ] Integrate with smart concatenation
- [ ] Add tests and documentation

**Acceptance Criteria:**
- ML model scores directories accurately
- Integration works with existing system
- Performance is acceptable
- Tests pass
- Documentation explains approach

---

#### Issue #10: Web Portal UI/UX Improvements
**Labels**: `enhancement`, `ux`, `frontend`  
**Priority**: Low  
**Estimated Effort**: 4-8 hours

**Description:**
Various UI/UX improvements based on user feedback and best practices.

**Tasks:**
- [ ] Collect user feedback
- [ ] Identify improvement areas
- [ ] Implement responsive design fixes
- [ ] Add keyboard shortcuts
- [ ] Improve accessibility
- [ ] Add dark mode option

**Acceptance Criteria:**
- UI improvements implemented
- Accessibility improved
- User feedback addressed
- Tests pass

---

## Issue Template Structure

When creating issues, use this template:

```markdown
## Description
[Clear description of the issue/enhancement]

## Motivation
[Why this is valuable]

## Proposed Solution
[How to implement it]

## Tasks
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Additional Context
[Any other relevant information]
```

---

## Issue Prioritization Guidelines

**High Priority:**
- Security issues
- Critical bugs
- Documentation gaps
- Good first issues for contributors

**Medium Priority:**
- Feature enhancements
- Performance improvements
- Developer experience improvements

**Low Priority:**
- Nice-to-have features
- Experimental features
- Long-term improvements

---

## Creating Issues Timeline

**Week 1 (Initial Release):**
- Create Issues #1, #2, #3 (good first issues)
- Create Issue #4 (feature enhancement)

**Week 2-3:**
- Create Issues #5, #6 (devops and UX)
- Monitor community feedback for additional issues

**Month 2+:**
- Create Issues #7-10 as needed
- Create issues based on community requests

---

## Notes

- All issues should be clearly labeled
- Good first issues should be well-documented
- Feature issues should include design considerations
- All issues should link to relevant documentation
- Consider creating issue templates in GitHub for consistency

---

## Maintenance Notes

**For Maintainers:**
- Use this document as a reference when creating GitHub issues
- Once an issue is created in GitHub, you can mark it here as "Created" with a link
- This document can be archived or removed once all planned issues are created
- Consider moving to `.github/` directory if you want it more visible to contributors

**For Contributors:**
- Check GitHub Issues for active work items
- This document is for planning purposes only
- If you want to work on something, check if a GitHub issue exists first

---

**Status**: Planning document - Ready for GitHub issue creation after open-source release

