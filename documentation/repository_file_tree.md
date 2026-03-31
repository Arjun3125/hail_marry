# Repository File Tree

This is the detailed project tree in the repo-style format you asked for.

Notes:
- This tree includes the current workspace files except hidden VCS/cache/build folders such as `.git`, `.venv`, `.pytest_cache`, `.pytest_tmp`, `pytest_tmp`, `node_modules`, and `.next`.
- Runtime data directories such as `data/`, `uploads/`, `vector_store/`, `raw/`, and `private_storage/` are listed only if files are present outside excluded caches.
- The goal here is file structure visibility, not subsystem explanation. Use `system_architecture_map.md` for the architecture view.

```text
proxy_notebooklm/
|-- .github
|   \-- workflows
|       |-- ci.yml
|       \-- production-readiness.yml
|-- all_documents
|   |-- action_split.md
|   |-- Admin review dashboard.md
|   |-- Admin Review Dashboard.md for AIaaS.txt
|   |-- AI engine deep design.md
|   |-- AI in Indian K-12 Learning.txt
|   |-- Android shell.md
|   |-- api_logs.txt
|   |-- api_reference.md
|   |-- Architecture.md
|   |-- Backup and recovery policy.md
|   |-- Below is a production-grade AI Engi.txt
|   |-- Below is a production-grade Archite.txt
|   |-- Below is a production-grade Filteri.txt
|   |-- Below is a production-grade Hosting.txt
|   |-- Below is a production-grade System.txt
|   |-- Below is a production-grade Tech St.txt
|   |-- Below is a production-grade UI Desi.txt
|   |-- business_analysis.md
|   |-- CHANGELOG.md
|   |-- competitor_analysis_mastersoft.txt
|   |-- CONTRIBUTING.md
|   |-- DPDP_COMPLIANCE.md
|   |-- error.txt
|   |-- error_seed.txt
|   |-- feature_guide.md
|   |-- Filtering logic.md
|   |-- Hosting and development env.md
|   |-- How to Document a Website Project.md
|   |-- implementation_plan.md
|   |-- MULTI_TIER_ROLLOUT_PLAN.md
|   |-- pip_freeze.txt
|   |-- pip_freeze_utf8.txt
|   |-- quickstart.md
|   |-- README.md
|   |-- requirements.txt
|   |-- Security checks.md
|   |-- Security Checks.md for AIaaS..txt
|   |-- Sitemap & Wireframe.md for AIaaS..txt
|   |-- Sitemap wireframe.md
|   |-- STAR_FEATURES_ANALYSIS.md
|   |-- startup_log.txt
|   |-- stderr.txt
|   |-- structural_audit.md
|   |-- System overview.md
|   |-- tb.txt
|   |-- tb2.txt
|   |-- Tech stack.md
|   |-- Testing.md
|   |-- timetable_generator_spec.md
|   |-- traceback.txt
|   |-- Ui design.md
|   |-- VidyaOs_feature_guide.md
|   |-- VidyaOS_Features_List.md
|   |-- whatsapp_access_implementation_plan.md
|   \-- whatsapp_integration.md
|-- backend
|   |-- alembic
|   |   |-- versions
|   |   |   |-- .keep
|   |   |   |-- 20260303_0001_add_unique_constraint_assignment_submissions.py
|   |   |   |-- 20260306_0002_enterprise_foundations.py
|   |   |   |-- 20260306_0003_add_ai_job_tables.py
|   |   |   |-- 20260307_0004_add_hashed_password_to_users.py
|   |   |   |-- 20260312_0005_add_qr_login_expiry.py
|   |   |   |-- 20260327_0006_create_notebooks_table.py
|   |   |   |-- 20260327_0007_add_notebook_id_to_tables.py
|   |   |   |-- 20260327_0008_create_generated_content_table.py
|   |   |   |-- 20260327_0009_add_notebook_id_to_kg_concepts.py
|   |   |   |-- 20260328_0010_add_tenant_id_to_notebooks_and_generated_content.py
|   |   |   |-- 20260331_0011_create_topic_mastery_table.py
|   |   |   |-- 20260331_0012_create_learner_profiles_table.py
|   |   |   |-- 20260331_0013_create_study_path_plans_table.py
|   |   |   \-- 20260331_0014_create_usage_counters_table.py
|   |   |-- env.py
|   |   \-- script.py.mako
|   |-- auth
|   |   |-- __init__.py
|   |   |-- dependencies.py
|   |   |-- jwt.py
|   |   |-- oauth.py
|   |   |-- scoping.py
|   |   \-- token_blacklist.py
|   |-- demo_pdfs
|   |   |-- English_Merchant_of_Venice.pdf
|   |   |-- History_Indian_Independence.pdf
|   |   |-- NCERT_Mathematics_Ch4_Quadratics.pdf
|   |   \-- NCERT_Science_Ch6_Photosynthesis.pdf
|   |-- locales
|   |   |-- en.json
|   |   |-- hi.json
|   |   \-- mr.json
|   |-- logs
|   |   |-- demo_backend_stderr.log
|   |   \-- demo_backend_stdout.log
|   |-- middleware
|   |   |-- __init__.py
|   |   |-- captcha.py
|   |   |-- csrf.py
|   |   |-- observability.py
|   |   |-- rate_limit.py
|   |   \-- tenant.py
|   |-- models
|   |   \-- __init__.py
|   |-- routes
|   |   \-- __init__.py
|   |-- schemas
|   |   |-- __init__.py
|   |   \-- common.py
|   |-- scripts
|   |   |-- __init__.py
|   |   |-- compute_performance.py
|   |   |-- download_ocr_fixtures.py
|   |   |-- index_docs.py
|   |   |-- ocr_benchmark_summary.py
|   |   |-- ocr_fixture_audit.py
|   |   \-- ocr_fixture_status.py
|   |-- services
|   |   \-- __init__.py
|   |-- src
|   |   |-- domains
|   |   |   |-- academic
|   |   |   |   |-- models
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- assignment.py
|   |   |   |   |   |-- attendance.py
|   |   |   |   |   |-- core.py
|   |   |   |   |   |-- lecture.py
|   |   |   |   |   |-- marks.py
|   |   |   |   |   |-- parent_link.py
|   |   |   |   |   |-- performance.py
|   |   |   |   |   |-- test_series.py
|   |   |   |   |   \-- timetable.py
|   |   |   |   |-- routes
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- parent.py
|   |   |   |   |   |-- students.py
|   |   |   |   |   \-- teacher.py
|   |   |   |   |-- schemas
|   |   |   |   |   \-- __init__.py
|   |   |   |   |-- services
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- digest_email.py
|   |   |   |   |   |-- gamification.py
|   |   |   |   |   |-- leaderboard.py
|   |   |   |   |   |-- report_card.py
|   |   |   |   |   |-- timetable_generator.py
|   |   |   |   |   |-- weakness_alerts.py
|   |   |   |   |   \-- whatsapp.py
|   |   |   |   |-- __init__.py
|   |   |   |   \-- router.py
|   |   |   |-- administrative
|   |   |   |   |-- models
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- admission.py
|   |   |   |   |   |-- billing.py
|   |   |   |   |   |-- complaint.py
|   |   |   |   |   |-- compliance.py
|   |   |   |   |   |-- fee.py
|   |   |   |   |   |-- incident.py
|   |   |   |   |   \-- library.py
|   |   |   |   |-- routes
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- admin.py
|   |   |   |   |   |-- admission.py
|   |   |   |   |   |-- billing.py
|   |   |   |   |   |-- fees.py
|   |   |   |   |   |-- library.py
|   |   |   |   |   \-- superadmin.py
|   |   |   |   |-- schemas
|   |   |   |   |   \-- __init__.py
|   |   |   |   |-- services
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- admission.py
|   |   |   |   |   |-- analytics_aggregator.py
|   |   |   |   |   |-- billing.py
|   |   |   |   |   |-- compliance.py
|   |   |   |   |   |-- fee_management.py
|   |   |   |   |   |-- incident_management.py
|   |   |   |   |   |-- library.py
|   |   |   |   |   \-- operations_center.py
|   |   |   |   |-- __init__.py
|   |   |   |   \-- router.py
|   |   |   |-- identity
|   |   |   |   |-- models
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- tenant.py
|   |   |   |   |   \-- user.py
|   |   |   |   |-- routes
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- auth.py
|   |   |   |   |   |-- enterprise.py
|   |   |   |   |   |-- invitations.py
|   |   |   |   |   \-- onboarding.py
|   |   |   |   |-- schemas
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- auth.py
|   |   |   |   |-- services
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- onboarding.py
|   |   |   |   |   |-- saml_sso.py
|   |   |   |   |   \-- team_invite.py
|   |   |   |   |-- __init__.py
|   |   |   |   \-- router.py
|   |   |   \-- platform
|   |   |       |-- models
|   |   |       |   |-- __init__.py
|   |   |       |   |-- ai.py
|   |   |       |   |-- ai_job.py
|   |   |       |   |-- audit.py
|   |   |       |   |-- document.py
|   |   |       |   |-- engagement.py
|   |   |       |   |-- feature_flag.py
|   |   |       |   |-- generated_content.py
|   |   |       |   |-- knowledge_graph.py
|   |   |       |   |-- learner_profile.py
|   |   |       |   |-- notebook.py
|   |   |       |   |-- notification.py
|   |   |       |   |-- observability.py
|   |   |       |   |-- spaced_repetition.py
|   |   |       |   |-- study_path_plan.py
|   |   |       |   |-- study_session.py
|   |   |       |   |-- topic_mastery.py
|   |   |       |   |-- usage_counter.py
|   |   |       |   |-- webhook.py
|   |   |       |   \-- whatsapp_models.py
|   |   |       |-- routes
|   |   |       |   |-- __init__.py
|   |   |       |   |-- ai_history.py
|   |   |       |   |-- ai_studio.py
|   |   |       |   |-- branding.py
|   |   |       |   |-- demo.py
|   |   |       |   |-- demo_management.py
|   |   |       |   |-- feature_flags.py
|   |   |       |   |-- generated_content.py
|   |   |       |   |-- i18n.py
|   |   |       |   |-- mascot.py
|   |   |       |   |-- notebooks.py
|   |   |       |   |-- notifications.py
|   |   |       |   |-- personalization.py
|   |   |       |   |-- support.py
|   |   |       |   \-- whatsapp.py
|   |   |       |-- schemas
|   |   |       |   |-- __init__.py
|   |   |       |   |-- ai_history.py
|   |   |       |   |-- ai_runtime.py
|   |   |       |   |-- feature_flags.py
|   |   |       |   |-- generated_content.py
|   |   |       |   \-- notebook.py
|   |   |       |-- services
|   |   |       |   |-- __init__.py
|   |   |       |   |-- ai_gateway.py
|   |   |       |   |-- ai_grading.py
|   |   |       |   |-- ai_queue.py
|   |   |       |   |-- alerting.py
|   |   |       |   |-- branding_extractor.py
|   |   |       |   |-- context_memory.py
|   |   |       |   |-- deployment_guidance.py
|   |   |       |   |-- doc_watcher.py
|   |   |       |   |-- docs_chatbot.py
|   |   |       |   |-- emailer.py
|   |   |       |   |-- feature_flags.py
|   |   |       |   |-- i18n.py
|   |   |       |   |-- knowledge_graph.py
|   |   |       |   |-- learner_profile_service.py
|   |   |       |   |-- llm_providers.py
|   |   |       |   |-- mascot_orchestrator.py
|   |   |       |   |-- mascot_registry.py
|   |   |       |   |-- mascot_schemas.py
|   |   |       |   |-- mascot_session_store.py
|   |   |       |   |-- mastery_tracking_service.py
|   |   |       |   |-- metrics_registry.py
|   |   |       |   |-- notifications.py
|   |   |       |   |-- observability_notifier.py
|   |   |       |   |-- plugin_registry.py
|   |   |       |   |-- runtime_scheduler.py
|   |   |       |   |-- sentry_config.py
|   |   |       |   |-- sms.py
|   |   |       |   |-- startup_checks.py
|   |   |       |   |-- structured_logging.py
|   |   |       |   |-- study_path_service.py
|   |   |       |   |-- telemetry.py
|   |   |       |   |-- trace_backend.py
|   |   |       |   |-- traceability.py
|   |   |       |   |-- usage_governance.py
|   |   |       |   |-- webhooks.py
|   |   |       |   |-- whatsapp_gateway.py
|   |   |       |   \-- worker_runtime.py
|   |   |       |-- __init__.py
|   |   |       \-- router.py
|   |   |-- infrastructure
|   |   |   |-- llm
|   |   |   |   |-- __init__.py
|   |   |   |   |-- cache.py
|   |   |   |   |-- embeddings.py
|   |   |   |   \-- providers.py
|   |   |   |-- vector_store
|   |   |   |   |-- __init__.py
|   |   |   |   |-- citation_linker.py
|   |   |   |   |-- connectors.py
|   |   |   |   |-- hyde.py
|   |   |   |   |-- ingestion.py
|   |   |   |   |-- ocr_service.py
|   |   |   |   |-- retrieval.py
|   |   |   |   \-- vector_store.py
|   |   |   \-- __init__.py
|   |   |-- interfaces
|   |   |   |-- rest_api
|   |   |   |   |-- ai
|   |   |   |   |   |-- routes
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- ai.py
|   |   |   |   |   |   |-- ai_jobs.py
|   |   |   |   |   |   |-- audio.py
|   |   |   |   |   |   |-- discovery.py
|   |   |   |   |   |   |-- documents.py
|   |   |   |   |   |   |-- openai_compat.py
|   |   |   |   |   |   \-- video.py
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- agent_orchestrator.py
|   |   |   |   |   |-- discovery_workflows.py
|   |   |   |   |   |-- ingestion_workflows.py
|   |   |   |   |   |-- router.py
|   |   |   |   |   |-- teacher_workflows.py
|   |   |   |   |   \-- workflows.py
|   |   |   |   |-- whatsapp
|   |   |   |   |   |-- agent.py
|   |   |   |   |   \-- router.py
|   |   |   |   \-- __init__.py
|   |   |   |-- whatsapp_bot
|   |   |   |   |-- __init__.py
|   |   |   |   \-- agent.py
|   |   |   \-- __init__.py
|   |   \-- shared
|   |       |-- ai_tools
|   |       |   |-- erp_tools.py
|   |       |   |-- study_tools.py
|   |       |   \-- whatsapp_tools.py
|   |       \-- ocr_imports.py
|   |-- tests
|   |   |-- evaluation
|   |   |   |-- __init__.py
|   |   |   |-- test_intent_classifier_benchmark.py
|   |   |   |-- test_ocr_benchmark.py
|   |   |   |-- test_personalization_benchmark.py
|   |   |   |-- test_ragas_evaluation.py
|   |   |   |-- test_retrieval_benchmark.py
|   |   |   \-- test_textbook_feature_grounding.py
|   |   |-- fixtures
|   |   |   \-- ocr
|   |   |       |-- .gitkeep
|   |   |       |-- classroom_board_001.jpg
|   |   |       |-- classroom_board_001.txt
|   |   |       |-- handwriting_messy_001.jpg
|   |   |       |-- handwriting_messy_001.txt
|   |   |       |-- handwriting_neat_001.jpg
|   |   |       |-- handwriting_neat_001.txt
|   |   |       |-- low_light_skew_001.jpg
|   |   |       |-- low_light_skew_001.txt
|   |   |       |-- manifest.csv
|   |   |       |-- mixed_en_hi_001.jpg
|   |   |       |-- mixed_en_hi_001.txt
|   |   |       |-- mixed_en_mr_001.jpg
|   |   |       |-- mixed_en_mr_001.txt
|   |   |       |-- mixed_hi_mr_001.jpg
|   |   |       |-- mixed_hi_mr_001.txt
|   |   |       |-- printed_english_001.jpg
|   |   |       |-- printed_english_001.txt
|   |   |       |-- printed_hindi_001.jpg
|   |   |       |-- printed_hindi_001.txt
|   |   |       |-- printed_marathi_001.jpg
|   |   |       |-- printed_marathi_001.txt
|   |   |       \-- README.md
|   |   |-- integration
|   |   |   \-- test_webhook_integration.py
|   |   |-- conftest.py
|   |   |-- test_admission.py
|   |   |-- test_agent_orchestrator.py
|   |   |-- test_ai_gateway_errors.py
|   |   |-- test_ai_query_routes.py
|   |   |-- test_ai_queue.py
|   |   |-- test_ai_studio_sessions.py
|   |   |-- test_alerting.py
|   |   |-- test_audit_fixes.py
|   |   |-- test_auth_qr_routes.py
|   |   |-- test_auth_security.py
|   |   |-- test_billing.py
|   |   |-- test_branding_routes.py
|   |   |-- test_captcha.py
|   |   |-- test_citations.py
|   |   |-- test_compliance.py
|   |   |-- test_config_validation.py
|   |   |-- test_connectors.py
|   |   |-- test_constants.py
|   |   |-- test_csrf_middleware.py
|   |   |-- test_doc_watcher.py
|   |   |-- test_docs_chatbot.py
|   |   |-- test_enterprise_routes.py
|   |   |-- test_feature_flags_routes.py
|   |   |-- test_fee_management.py
|   |   |-- test_file_uploads.py
|   |   |-- test_gamification.py
|   |   |-- test_hyde.py
|   |   |-- test_i18n.py
|   |   |-- test_incident_management.py
|   |   |-- test_infra_utils.py
|   |   |-- test_knowledge_graph.py
|   |   |-- test_leaderboard.py
|   |   |-- test_library.py
|   |   |-- test_llm_providers_ollama_failover.py
|   |   |-- test_mascot_routes.py
|   |   |-- test_mascot_whatsapp_adapter.py
|   |   |-- test_metrics_registry.py
|   |   |-- test_normalize_tool_output.py
|   |   |-- test_notebook_job_scope_regressions.py
|   |   |-- test_notebook_retrieval.py
|   |   |-- test_notebook_tenant_scope.py
|   |   |-- test_notifications.py
|   |   |-- test_ocr_audit.py
|   |   |-- test_ocr_integration.py
|   |   |-- test_ocr_route_metadata.py
|   |   |-- test_onboarding.py
|   |   |-- test_openai_compat.py
|   |   |-- test_openai_compat_routes.py
|   |   |-- test_personalization_learning.py
|   |   |-- test_pipeline_stage_metrics.py
|   |   |-- test_plugin_registry.py
|   |   |-- test_queue_resiliency.py
|   |   |-- test_rate_limit.py
|   |   |-- test_redis_split.py
|   |   |-- test_report_card.py
|   |   |-- test_runtime_ops.py
|   |   |-- test_security_regressions.py
|   |   |-- test_sm2_algorithm.py
|   |   |-- test_structured_tool_output_contracts.py
|   |   |-- test_team_invite.py
|   |   |-- test_tenant_middleware.py
|   |   |-- test_token_blacklist.py
|   |   |-- test_traceability.py
|   |   |-- test_upload_security.py
|   |   |-- test_usage_governance.py
|   |   |-- test_weakness_alerts.py
|   |   |-- test_webhooks.py
|   |   |-- test_whatsapp.py
|   |   |-- test_whatsapp_gateway.py
|   |   |-- test_whatsapp_integration.py
|   |   \-- test_whatsapp_media_queue_failures.py
|   |-- uploads
|   |   |-- 00000000000000000000000000000001_00000000000000000000000000000020_101c6cf51bfb470586e756c15c5cb2d3_NCERT_Science_Ch6_Photosynthesis.pdf
|   |   |-- 00000000000000000000000000000001_00000000000000000000000000000020_320e1d949bc34a40bfa75c5c3882abe6_English_Merchant_of_Venice.pdf
|   |   |-- 00000000000000000000000000000001_00000000000000000000000000000020_c619fe810db2448ea3690efea47bd157_History_Indian_Independence.pdf
|   |   |-- 00000000000000000000000000000001_00000000000000000000000000000020_d2211c778a77473482873fd5a19d9129_NCERT_Mathematics_Ch4_Quadratics.pdf
|   |   |-- 09ca1175-6c47-45f6-9de3-2df1f87c7470_3eb7dc03-654f-42d5-b8c1-4bd023e42764_notes.pdf
|   |   |-- 21d705f5-000e-4cee-9d60-80f935032c50_effed64b-edbf-443b-9046-fbd3139c1252_194ce7627bb941e798a9122f4bae3015_notes.pdf
|   |   |-- 2c76c1bf-b0bb-4e79-bcae-e6fdc989d64e_cb700c0a-79ea-434a-a137-0ab7ca57b5f4_572ef07894dc4c779adbc653dbde8275_notes.pdf
|   |   |-- 408d8e97-9af0-46b2-ab28-9db2e3b64fe4_234cc9f7-dd56-4633-918e-acaa23042c53_notes.pdf
|   |   |-- 44e38ea3-9d04-450c-b8f6-91e00f9cb032_ec63a69b-dbe5-4980-ac23-bc33c32d2399_f8249473996a4d99b994ac43d956899f_notes.pdf
|   |   |-- 631fef9f-b4fc-4b35-b6e6-9f79abbe6c1f_158890bf-aa9f-4697-a055-63c6da5d2850_0b46715f626340aea71c5e6dfe9ea8c8_notes.pdf
|   |   |-- 783d0296-e85e-44cd-af75-ee1f3abfe8aa_64102fdf-6505-4921-9bbd-8beb5eb13347_12a3fb6ae21a4e42ad9a113e83ad04ba_notes.pdf
|   |   |-- 8507232f-88ed-44d7-998c-a1f0730008e7_4536b153-fda0-4078-b602-537e7f5f6c23_35d099f80c434b0ca6cc8d55a21c1e83_notes.pdf
|   |   |-- 90ce7d5a-2dbd-46a7-862c-cf2d2624ca6e_b01cfb77-f139-4961-9f28-0af4741c31fe_notes.pdf
|   |   |-- 93782f9c-e3d3-4c5c-b890-0d55b9bf4771_8bb84e53-eb92-490c-a8df-e7868998d97f_98c5372c424e41abbe9a8440c6e1803c_notes.pdf
|   |   |-- a09ea284-c890-435e-a8ab-c4050f9ba802_9a538919-dce7-460b-9421-142140bf1505_notes.pdf
|   |   |-- c22a851a-1502-44ef-87f9-c6fb71478f12_b54135b2-6a4f-4b10-84a1-8143754c2131_3eed89ca8109405b92e8664a38090e20_notes.pdf
|   |   |-- cd5af30d-d40b-493f-ad54-49899562ffd0_80fb26be-ad8c-4630-a052-4bc5ddada2ea_notes.pdf
|   |   \-- f81f5c25-b35d-4068-8b88-19ca13f989e8_1070dc74-c01c-48b2-b26a-31170fc6c985_notes.pdf
|   |-- utils
|   |   |-- __init__.py
|   |   |-- pagination.py
|   |   \-- upload_security.py
|   |-- vector_store
|   |   \-- tenant_00000000000000000000000000000001.pkl
|   |-- .coverage
|   |-- .dockerignore
|   |-- ai_worker.py
|   |-- alembic.ini
|   |-- check_ai_queries.py
|   |-- config.py
|   |-- constants.py
|   |-- create_demo_pdfs.py
|   |-- database.py
|   |-- demo.db
|   |-- demo_local.err.log
|   |-- demo_local.out.log
|   |-- demo_seed.py
|   |-- demo_server.err.log
|   |-- demo_server.log
|   |-- Dockerfile
|   |-- Dockerfile.worker
|   |-- error.txt
|   |-- error_seed.txt
|   |-- features_catalog.json
|   |-- generate_demo_ai_history.py
|   |-- generate_real_ai_queries.py
|   |-- ingest_demo_pdfs.py
|   |-- ingest_pdfs_simple.py
|   |-- ingest_standalone.py
|   |-- main.py
|   |-- models.py
|   |-- pip_freeze.txt
|   |-- pip_freeze_utf8.txt
|   |-- requirements.txt
|   |-- seed.py
|   |-- settings-production.yaml
|   |-- settings.yaml
|   |-- show_sample_responses.py
|   |-- start-api.sh
|   |-- start-worker.sh
|   |-- startup_log.txt
|   |-- stderr.txt
|   |-- tb.txt
|   |-- tb2.txt
|   |-- test.db
|   |-- test_out.txt
|   |-- test_out_utf8.txt
|   |-- test_output.log
|   |-- traceback.txt
|   |-- update_catalog.py
|   |-- vidyaos.db
|   |-- vidyaos_demo.db
|   |-- vidyaos_demo.db.bak
|   \-- worker_health_app.py
|-- compliance_exports
|   \-- None.zip
|-- data
|   |-- ss
|   |   \-- file.png
|   |-- BUILD_DOCUMENTATION.md
|   |-- product_presentation.md.resolved
|   \-- Untitled document.txt
|-- documentation
|   |-- system_docs
|   |   |-- Admin review dashboard.md
|   |   |-- AI engine deep design.md
|   |   |-- Android shell.md
|   |   |-- Architecture.md
|   |   |-- Backup and recovery policy.md
|   |   |-- Database schema.md
|   |   |-- Filtering logic.md
|   |   |-- Hosting and development env.md
|   |   |-- Security checks.md
|   |   |-- Sitemap wireframe.md
|   |   |-- System overview.md
|   |   |-- Tech stack.md
|   |   |-- Testing.md
|   |   \-- Ui design.md
|   |-- action_split.md
|   |-- AI in Indian K-12 Learning.txt
|   |-- api_reference.md
|   |-- demo_quality_master_plan.md
|   |-- detailed_test_suite_blueprint.md
|   |-- DPDP_COMPLIANCE.md
|   |-- full_system_audit_report.md
|   |-- implementation_completion_summary.md
|   |-- mascot_phase4_whatsapp_plan.md
|   |-- mascot_production_execution_checklist.md
|   |-- mascot_production_upgrade_plan.md
|   |-- mascot_release_gate.md
|   |-- mascot_release_gate_evidence_template.md
|   |-- mascot_whatsapp_staging_evidence_template.md
|   |-- mascot_whatsapp_staging_manual_test_script.md
|   |-- mitigation_execution_plan.md
|   |-- ocr_benchmark_report.md
|   |-- ocr_fixture_collection_guide.md
|   |-- ocr_implementation_completion_summary.md
|   |-- ocr_manual_qa_script.md
|   |-- ocr_system_audit_report.md
|   |-- ocr_universal_input_execution_checklist.md
|   |-- ocr_universal_input_implementation_plan.md
|   |-- personalization_feature_ux_evaluation_report.md
|   |-- personalization_learning_execution_checklist.md
|   |-- personalization_learning_upgrade_plan.md
|   |-- product_improvement_report.md
|   |-- production_certification_execution_checklist.md
|   |-- production_certification_implementation_plan.md
|   |-- production_readiness_audit_report.md
|   |-- quickstart.md
|   |-- rag_feature_evaluation_report.md
|   |-- rag_feature_execution_checklist.md
|   |-- structural_audit.md
|   |-- student_account_operational_cost_report.md
|   |-- system_architecture_map.md
|   |-- timetable_generator_spec.md
|   |-- traceability_diagnostics_framework.md
|   |-- usage_governance_framework.md
|   |-- whatsapp_access_implementation_plan.md
|   |-- whatsapp_integration.md
|   |-- whatsapp_media_ingestion_report.md
|   |-- whatsapp_release_gate.md
|   |-- whatsapp_staging_evidence_template.md
|   |-- whatsapp_staging_manual_test_script.md
|   |-- whatsapp_tier_4_5_execution_checklist.md
|   \-- whatsapp_tier_4_5_upgrade_plan.md
|-- frontend
|   |-- frontend
|   |   |-- frontend
|   |   |   \-- test-results
|   |   |       |-- ai-studio-mobile.png
|   |   |       |-- demo-home-mobile.png
|   |   |       \-- student-overview-mobile.png
|   |   |-- test-results
|   |   |   |-- ai-studio-assistant-ui.png
|   |   |   |-- ai-studio-check.png
|   |   |   |-- ai-studio-fixed.png
|   |   |   |-- ai-studio-mobile.png
|   |   |   |-- ai-studio-upgraded.png
|   |   |   |-- demo-home-mobile.png
|   |   |   |-- demo-home.png
|   |   |   |-- demo-student.png
|   |   |   |-- student-ai-unified.png
|   |   |   |-- student-overview-live.png
|   |   |   \-- student-overview-mobile.png
|   |   |-- test-results_student_ai-studio.png
|   |   |-- test-results_student_ai.png
|   |   |-- test-results_student_assignments.png
|   |   |-- test-results_student_overview.png
|   |   \-- test-results_student_timetable.png
|   |-- public
|   |   |-- .well-known
|   |   |   \-- assetlinks.json
|   |   |-- brand
|   |   |   \-- logo-mark.png
|   |   |-- images
|   |   |   \-- mh-logo.png
|   |   |-- file.svg
|   |   |-- globe.svg
|   |   |-- manifest.json
|   |   |-- next.svg
|   |   |-- sw.js
|   |   |-- vercel.svg
|   |   \-- window.svg
|   |-- src
|   |   |-- app
|   |   |   |-- admin
|   |   |   |   |-- ai-review
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- ai-usage
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- assistant
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- billing
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- branding
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- classes
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- complaints
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- dashboard
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- enterprise
|   |   |   |   |   |-- compliance
|   |   |   |   |   |   \-- page.tsx
|   |   |   |   |   |-- incidents
|   |   |   |   |   |   \-- page.tsx
|   |   |   |   |   \-- sso
|   |   |   |   |       \-- page.tsx
|   |   |   |   |-- feature-flags
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- qr-cards
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- queue
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- reports
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- security
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- settings
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- setup-wizard
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- timetable
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- traces
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- users
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- webhooks
|   |   |   |   |   \-- page.tsx
|   |   |   |   \-- layout.tsx
|   |   |   |-- demo
|   |   |   |   \-- page.tsx
|   |   |   |-- login
|   |   |   |   \-- page.tsx
|   |   |   |-- parent
|   |   |   |   |-- assistant
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- attendance
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- dashboard
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- reports
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- results
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- layout.tsx
|   |   |   |   \-- page.tsx
|   |   |   |-- qr-login
|   |   |   |   \-- page.tsx
|   |   |   |-- student
|   |   |   |   |-- ai
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- ai-library
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- ai-studio
|   |   |   |   |   |-- components
|   |   |   |   |   |   |-- ActionBar.tsx
|   |   |   |   |   |   |-- AIMessageRenderer.tsx
|   |   |   |   |   |   |-- Animations.tsx
|   |   |   |   |   |   |-- CitationPopover.tsx
|   |   |   |   |   |   |-- CommandPalette.tsx
|   |   |   |   |   |   |-- ContextPanel.tsx
|   |   |   |   |   |   |-- EditableNotesSurface.tsx
|   |   |   |   |   |   |-- FlashcardDeck.tsx
|   |   |   |   |   |   |-- FocusMode.tsx
|   |   |   |   |   |   |-- KnowledgeGraphView.tsx
|   |   |   |   |   |   |-- LearningWorkspace.tsx
|   |   |   |   |   |   |-- MermaidDiagram.tsx
|   |   |   |   |   |   |-- MindMapCanvas.tsx
|   |   |   |   |   |   |-- NotebookSelector.tsx
|   |   |   |   |   |   |-- ProgressTracker.tsx
|   |   |   |   |   |   |-- QuizView.tsx
|   |   |   |   |   |   |-- SmartSuggestions.tsx
|   |   |   |   |   |   |-- threadPersistence.ts
|   |   |   |   |   |   \-- ToolRail.tsx
|   |   |   |   |   |-- hooks
|   |   |   |   |   |   \-- useKeyboardShortcuts.ts
|   |   |   |   |   |-- ai-studio.css
|   |   |   |   |   |-- IMPLEMENTATION_STATUS.md
|   |   |   |   |   |-- page.tsx
|   |   |   |   |   \-- REDESIGN_PLAN.md
|   |   |   |   |-- assignments
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- assistant
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- attendance
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- audio-overview
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- complaints
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- leaderboard
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- lectures
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- mind-map
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- overview
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- profile
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- results
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- reviews
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- timetable
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- tools
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- upload
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- video-overview
|   |   |   |   |   \-- page.tsx
|   |   |   |   \-- layout.tsx
|   |   |   |-- teacher
|   |   |   |   |-- assignments
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- assistant
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- attendance
|   |   |   |   |   |-- AttendanceClient.tsx
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- classes
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- dashboard
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- discover
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- doubt-heatmap
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- generate-assessment
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- insights
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- marks
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- profile
|   |   |   |   |   \-- page.tsx
|   |   |   |   |-- upload
|   |   |   |   |   \-- page.tsx
|   |   |   |   \-- layout.tsx
|   |   |   |-- favicon.ico
|   |   |   |-- globals.css
|   |   |   |-- layout.tsx
|   |   |   \-- page.tsx
|   |   |-- components
|   |   |   |-- dashboard
|   |   |   |   \-- GuidedStart.tsx
|   |   |   |-- mascot
|   |   |   |   |-- MascotActionResultCard.tsx
|   |   |   |   |-- MascotAssistantPage.tsx
|   |   |   |   |-- MascotConfirmationCard.tsx
|   |   |   |   |-- MascotLauncher.tsx
|   |   |   |   |-- MascotMessageList.tsx
|   |   |   |   |-- MascotPanel.tsx
|   |   |   |   |-- MascotShell.tsx
|   |   |   |   |-- MascotSuggestionChips.tsx
|   |   |   |   \-- types.ts
|   |   |   |-- providers
|   |   |   |   \-- QueryProvider.tsx
|   |   |   |-- theme
|   |   |   |   |-- BrandingProvider.tsx
|   |   |   |   |-- ThemeProvider.tsx
|   |   |   |   \-- ThemeToggle.tsx
|   |   |   |-- ui
|   |   |   |   |-- AIFallbackNotice.tsx
|   |   |   |   |-- button.tsx
|   |   |   |   |-- dropdown-menu.tsx
|   |   |   |   |-- ErrorRemediation.tsx
|   |   |   |   |-- HelpOverlay.tsx
|   |   |   |   \-- SharedUI.tsx
|   |   |   |-- AIErrorState.tsx
|   |   |   |-- AIHistorySidebar.tsx
|   |   |   |-- DemoToolbar.tsx
|   |   |   |-- DemoToolbarWrapper.tsx
|   |   |   |-- EmptyState.tsx
|   |   |   |-- GuidedTour.tsx
|   |   |   |-- RoleStartPanel.tsx
|   |   |   |-- ScreenReaderAnnouncer.tsx
|   |   |   |-- Sidebar.tsx
|   |   |   |-- Skeleton.tsx
|   |   |   \-- Toast.tsx
|   |   |-- i18n
|   |   |   |-- en.json
|   |   |   |-- hi.json
|   |   |   \-- LanguageProvider.tsx
|   |   \-- lib
|   |       |-- api.ts
|   |       |-- auth.tsx
|   |       |-- errorRemediation.ts
|   |       \-- utils.ts
|   |-- test-results
|   |   \-- .last-run.json
|   |-- tests
|   |   \-- e2e
|   |       |-- admin-dashboard.spec.ts
|   |       |-- admin-queue.spec.ts
|   |       |-- mascot-assistant.spec.ts
|   |       |-- ocr-review-flows.spec.ts
|   |       |-- smoke.spec.ts
|   |       |-- student-learning-flows.spec.ts
|   |       \-- teacher-academic-imports.spec.ts
|   |-- .dockerignore
|   |-- .env.local
|   |-- .gitignore
|   |-- capacitor.config.ts
|   |-- components.json
|   |-- demo_frontend.err.log
|   |-- demo_frontend.log
|   |-- Dockerfile
|   |-- Dockerfile.demo
|   |-- eslint.config.mjs
|   |-- next-env.d.ts
|   |-- next.config.ts
|   |-- package-lock.json
|   |-- package.json
|   |-- playwright.config.ts
|   |-- postcss.config.mjs
|   |-- README.md
|   |-- tsconfig.json
|   \-- tsconfig.tsbuildinfo
|-- ops
|   \-- observability
|       |-- grafana
|       |   \-- provisioning
|       |       |-- dashboards
|       |       |   |-- json
|       |       |   |   |-- aiaas-overview.json
|       |       |   |   \-- gpu-overview.json
|       |       |   \-- dashboards.yml
|       |       \-- datasources
|       |           \-- datasources.yml
|       |-- alert_rules.yml
|       |-- loki-config.yml
|       |-- prometheus.yml
|       |-- promtail-config.yml
|       \-- tempo.yml
|-- private_storage
|   \-- uploads
|       |-- mascot
|       |   |-- 071570c5-80e9-4c87-adf7-0656eb1e3f27_2692e42a-892c-403d-88f8-b608bcc91415_eb3365f737bf455c8ca82ff6e58dddab_notes.pdf
|       |   |-- 1443de03-0c07-4fcf-9469-c692bb02f7cf_d99e0957-e0f5-4f9d-8ce8-7395abf24931_ff858ec3c5e940fc822c80b2075b9a5d_lecture.pdf
|       |   |-- 1d060d6f-ba11-4574-a4ce-116ae9472df8_3a55b3df-eecc-48c8-92b2-88e1941937f3_8cb4c340d27444e6b6776643f0330414_lecture.pdf
|       |   |-- 21088ad6-38bf-472e-b2cb-d876e8a05145_0d1adac6-553b-45a4-9a3a-08b2618d78fd_4895453fb2744ba0ac94627a84fbb66d_notes.pdf
|       |   |-- 2697e1c1-e782-4b52-bc2f-14688b026394_c5b98804-8127-4b30-8347-0bd1324fbcf0_8ccb4f93122c44b7baad47a8767753c5_lecture.pdf
|       |   |-- 26b1740d-219c-4ca8-a85a-c4fa735c68be_4a5ad216-2c00-4448-8613-47efeddfe4b5_f178d18028e84c609cf600d912c2bb17_notes.pdf
|       |   |-- 28b375db-52b7-4774-a06d-b8039480a669_f5c36865-5981-4e8b-8945-db5aa17b79d3_41ccab51602840579aec179164f6c016_lecture.pdf
|       |   |-- 295595bd-a076-427c-be7e-b5399b5c7b8f_41be2879-05bb-4b24-82e6-63e6fa711384_f5aaa3278757426c9a4488ad6b51127c_notes.pdf
|       |   |-- 2b2ae07c-50df-4149-a096-03c32f8e624a_80988c9a-9f66-42ad-91e0-53d6589c34c7_c325ddd50db742e88f2874f70d3cd08b_lecture.pdf
|       |   |-- 2d1e1c5b-1ba4-4c88-9b49-ecfc7fe0220d_58927050-ba7a-4ec5-bc22-684b5ade36e7_7480bc8d530542809aa22f8c9ef59fc6_lecture.pdf
|       |   |-- 371b0e88-58a0-4114-baad-9f26f704306e_d72fdc1f-9877-4f9d-92ba-4aa36225db7f_08cc34985540465385da06ce6be0acb8_notes.pdf
|       |   |-- 376967b2-4d3b-447f-b617-68ad0c45924d_9dc4b3eb-0de4-4722-8cd8-008b24a6aa49_19773dfdac094c399970b6a57772a805_lecture.pdf
|       |   |-- 435b7354-db5b-40d4-9fe5-66e4273c2e4b_b139f354-0422-4f25-8a2e-b2c4939b8831_77140a4dff3f4c57b9f2b7052683da5e_lecture.pdf
|       |   |-- 48ff4db6-d52f-4305-aa00-d85b7bd93476_f175e79c-8a42-4839-9b29-e4ed86f96fb5_921c30c736944e8e9ca72704824c8386_lecture.pdf
|       |   |-- 4adc6f72-4d8c-4825-952f-8f8a401a2c4c_4005c21b-79cb-45aa-8925-4e828c2ff192_bde496285cef46bbbd6a6f55513cb08f_lecture.pdf
|       |   |-- 4e3ea7e9-bbbe-4cea-b452-41b7b05def56_29837cdc-9865-441d-b94b-7b118b0920fe_a6044a0630e14894ae46e08d19f42583_lecture.pdf
|       |   |-- 55e624bc-0d9a-4b96-9832-dadd65efb0f9_d4efdc2d-8f0b-4bc3-9531-e5e714f0a1bd_4885dbd994d646b7bd16b0a5b86d40fc_lecture.pdf
|       |   |-- 5649e348-e8be-4375-8f54-d4e0b4fa7df9_dc479858-6824-45b0-ba6a-3cb617c0d74a_d9e79a3d40544d96a2ebe60e2912f75a_lecture.pdf
|       |   |-- 5dacf99a-a7e0-49f1-9f39-67cafd42c870_934401bd-d1f6-45ff-b971-8976e8f65170_136a7e8ce624448fa7c5f1ec95b19eb2_notes.pdf
|       |   |-- 5f5cc3cb-34a6-4bd0-8dc9-3201d73c5b61_84d62d3e-3176-4c52-8917-42e58b0d40ad_95d3f629bfbe4936ba7764da43e7edaf_lecture.pdf
|       |   |-- 61238f14-e6f4-4347-8802-22c72deaf53d_6251eb71-32d6-48e3-a1ae-7239bc06b129_f1db2ffe626b4519ad7d8a169bfa411f_notes.pdf
|       |   |-- 6e478401-90a4-4282-8f47-8818ef9a7e80_3df120c6-99cc-4eac-818d-47229bb106b5_ec82f04b514f49a4832ada5ea90c2331_lecture.pdf
|       |   |-- 76ce068a-b15a-4da6-9884-2aed29a9e716_35a5b111-c12d-451f-9859-c62aa643bb47_4ef7d8af847b4b4d84124697d19000f6_lecture.pdf
|       |   |-- 770ea1c0-77e0-45d8-bdad-3ddc5f4cf25a_5addd13a-1029-44e6-a64e-c1abae73ac38_d202593db38a4a118002c5ad3c9c7dab_notes.pdf
|       |   |-- 7eb81f50-f172-462a-8bd0-f3b22d725829_23a72879-3b33-4853-9ad4-bec199b675a5_13f16373e7cc422a9dcefd7006945ba2_lecture.pdf
|       |   |-- 812aa8f5-aaf8-4822-8b23-29482704fa76_9b1287c7-180a-4ed1-b5a3-4a8e792c1570_0eef7ad026394e3d956849a82ef2298f_lecture.pdf
|       |   |-- 8383ce20-d685-430e-a0b8-7abf1948bce9_4e98737e-27de-45db-b621-a48edee663c7_1b0b50a3d9934eeeb30bab8af1ac48d9_lecture.pdf
|       |   |-- 898f2b63-c514-4443-bc2b-2d0a9c868a37_3f1b1724-9612-42c6-a5cf-b07522aa2dad_6d54048a9af544de93602dad3e6994f9_notes.pdf
|       |   |-- 8c989ef6-ff01-4769-ae3e-e64ddffbe9b0_762427e8-a525-409c-a6a3-23beacc8a3c2_c81600cc199c4f6e81c6857081d6ccb8_lecture.pdf
|       |   |-- 8f683c09-4fa0-4835-b5fd-84faf63a7039_6adac220-33df-48b1-ad5c-0c0268b9ccef_db43e1d51e8c4455b99e1281805c66a7_lecture.pdf
|       |   |-- 91c121c8-bb18-4d9d-899c-72e0d7e5f6f8_d7e4fcb5-7160-49e8-b10a-850697dbaeb0_ae024cb5ee9749afbdfa26c5090a29eb_lecture.pdf
|       |   |-- 927bcfab-4339-4051-98af-9f58bc2da148_a87af110-a53d-4e17-ac92-6e14194199fc_fcd60e14dae548b38930f6bb0d8db991_lecture.pdf
|       |   |-- 93f95afd-0ee4-49b8-87ac-19e9d08d3c42_08b53a24-0167-4ec5-93b4-393b8190e3dc_0fad429ffd764ac1b04e75f580538ed0_lecture.pdf
|       |   |-- 96f5aa30-71ce-4871-a0e8-598c58f4a38a_ab7a00ef-ed24-4e3f-b19b-3ea12fd472ea_358519dd50c84aa5b12a8f306cc7c608_notes.pdf
|       |   |-- 9b4a3d38-cee5-42c1-9703-eefdf16c73f5_a493d1ce-9d8e-4f92-9926-8bb82ff68b98_87fbbfe76b6b44f6bbf35ac22fc7f8e3_lecture.pdf
|       |   |-- a42f1898-a209-42f2-a3c6-549a60268c8a_536bf87c-3e6a-4012-9b49-a8a99956cd94_e72f697804b642ada81a345e12b12c94_lecture.pdf
|       |   |-- a643c68e-089b-4776-9f12-259e7adde249_34b45e72-8601-415b-ad72-0914ac8132f5_a0b6850d67454017b82e0a0400a9fb2a_lecture.pdf
|       |   |-- a94681fd-1da3-4bd9-bca3-6076b87b8da2_9b0dc5c5-4f3b-4f71-9ac3-9209326ec409_f40a8ee24e5c4afda67f3de59a6e2d20_notes.pdf
|       |   |-- ae39fac6-59b3-4c5f-9a69-7f7e3b4ed0d8_de8569e0-38ec-428a-b0a0-1fec866bc984_463affba71984cd4acdabee2b16284bc_lecture.pdf
|       |   |-- b22ef1a3-94b7-4dab-a8fa-c4ffe0672685_f44cf41d-fc39-410c-b06d-8798823268f9_abe571db87cd4496a12e6985fc6fa5ca_lecture.pdf
|       |   |-- b5f7f6f3-be1a-464c-b613-14aa70436d51_0a839766-0e7c-4720-b7de-48975ae50778_3edcdc517aaa4018a53322bfcff5364d_notes.pdf
|       |   |-- b6ba03ae-978e-4295-806d-7e66852ec4e6_35561164-151b-455a-be30-3e6409229e3c_bfdc84c09ce64620889a6f7e74775ddb_notes.pdf
|       |   |-- b8b71b04-7770-4613-b9c6-342f67460256_4ed347fe-179b-4c58-9492-d74e380053ae_018d884cce5344208e7f9df0ac3c7189_lecture.pdf
|       |   |-- bd09e73b-2501-4dc9-85fd-983259c4572b_c51592be-de67-4f77-ae67-b63517d02981_c1504eda2a644996bb128670d9d0015f_notes.pdf
|       |   |-- c5a865d3-e3d7-45e8-9934-0149dac5ee28_1cc4a5f4-8367-49ed-af4f-e0e4977198c6_686f41c454f7425da0ac1f9d98eda8a0_lecture.pdf
|       |   |-- c89a38e0-5714-40e1-b515-eb2688d01a4e_4f8d34c9-37fb-411a-8622-3412e808f23d_f80f34cb0203474c9871219ec28c75e0_lecture.pdf
|       |   |-- ca64a2a8-6a57-4f78-9d07-4d750b64ca5c_2b589916-e3ec-400c-9fbe-4047050d5c17_5cdc89bc43784a4c9b632dbcdc3249d0_lecture.pdf
|       |   |-- cc0b7977-a652-4a95-87ef-00dcfd2bb032_e9e3e7c4-238d-4245-a29c-5aa8b3ef9017_c758393dd3814f8080a0ef65bae7a1c7_lecture.pdf
|       |   |-- cde2859d-abbd-4076-8c2f-a7b2474c45de_12630b86-ee70-4bb1-a975-73aadef3287f_bb02cc3fa4ff4f36b0f3b5d12f2a7bee_lecture.pdf
|       |   |-- d6e6d622-c051-40ab-9d95-a27dd4380733_305a59a9-4ebf-4185-9ee0-63d024b1ceb3_0e718a1d387e40a5a8a6bd39f962cc5e_notes.pdf
|       |   |-- d7050062-0929-46cb-b55b-d72cb4de3d47_5ec6bce5-dee0-43f2-8f51-35539eb6445b_d3c261c261ca41169209d142c5fd62fd_notes.pdf
|       |   |-- dea84749-f53d-4578-983d-a4c28a2bcb4e_ecb46c78-4469-471e-a1a3-0ab7fe97a8a4_d04fd86b78444d59a2931f33410485e4_lecture.pdf
|       |   |-- e82cbe2f-9fde-4669-b6c8-79647fc9a3a1_d8c1c3bb-dae1-4835-93f9-0ad4c00012b2_dbaaf727720246ef824011919a4a5ca7_lecture.pdf
|       |   |-- e952c392-b7fb-46e8-afbf-f8202b02b582_9477d752-9353-4cf3-9696-d96aced77b1d_9df606ef73b04e1f8a8047b31f21e0cb_lecture.pdf
|       |   |-- f1e3d73c-305b-4136-aa36-e9f150d7fa8a_8ac1aa2d-0d0c-4958-9606-190ca806f649_8f3e42957ff54536ae86ca7ee03b3089_lecture.pdf
|       |   \-- f71be6c8-4009-4ee1-a94e-25cfec440e0d_bc481c09-d12e-4d62-ab78-348eed3b1913_c84ae74f85b24337b4e6a6e02c150eae_lecture.pdf
|       |-- 00e57aaa-88e0-473c-a673-5bda2dc96965_75b0d759-0192-4189-a087-14191566bb6e_1149e02cee5444369817197ea0b7f8e9_notes.pdf
|       |-- 02a6ea21-aa37-447b-a8f0-602519a60172_57eb7c46-107d-4489-a3b8-eed6b0920f23_5aa299ffc9594cc884ed7da3bdbe6fe9_notes.pdf
|       |-- 049fe477-2ecf-427a-8055-43b0c6e5916a_5e978f39-2cb8-403c-98e2-b98552cca314_723796b098134a7d826875a8de424ff1_notes.pdf
|       |-- 0780eee1-87d9-4b43-aa63-7da47671de8d_51e62d13-ec7c-468e-b022-ebe70921acf5_5a23809e8d4a4f888d1a820ad7704555_notes.pdf
|       |-- 09cf79d4-fbde-499c-9fc6-7f7ead17d192_2888a9b1-b29e-4d69-99ee-ed3f4345b4a1_13c5de6732fc428b816bf297cd242b55_notes.pdf
|       |-- 0a3ca97d-c4e8-4f29-9c93-aac8be5fd579_83c8a0ba-aa50-4232-ad8b-b946017bdd2b_e3d9404d9d7c4b88ad71687c167948d6_notes.pdf
|       |-- 0b5ecc3e-b0b6-44d5-ad54-cf7a397eb060_e707199b-2e17-484d-9b31-9d7e79e95232_78c300dec2b04da49885a15c76cb93aa_notes.pdf
|       |-- 0bfab1ca-8e82-4daf-8576-16c1dc04fd38_88c5b255-6afd-436e-83d0-068aa6b162be_d7e94ed085a3484ea7801694c0ba0c35_notes.pdf
|       |-- 0da98a78-b15e-48d8-983d-b403b5f4cd9d_2653061d-504b-4e8f-94de-9e713f50eeb7_d874516d12504f008ff855de08a002e3_notes.pdf
|       |-- 116ed63e-0c25-4e1a-87a1-2349be757380_330d5414-9e1f-4b2b-9e0b-a306c47ab5e2_2616e24834b542bd87da4036a2ea7012_notes.pdf
|       |-- 144db69d-8989-4784-889e-a0c7e6239479_dce900f1-5c78-44e1-ab0c-4eb9bc860564_456e796c09294d948559297f8c8948cb_notes.pdf
|       |-- 1544f94e-b335-468a-b2b0-31378267d455_9c3a2d8e-3bf6-4ac0-b630-861f3176b761_e014f6ae340d4c349e808fd38c470279_notes.pdf
|       |-- 16d30dce-76af-472a-a567-3250f5950803_1671c596-714a-445f-9084-ae416b90389a_a936dc17653d460f913616661b590559_notes.pdf
|       |-- 19c8adc7-abb7-412b-acac-f45554c6634b_afc1da10-d51c-4cb4-b29f-405244eec29c_aa841a9ddc9b47878860e12197a8289b_notes.pdf
|       |-- 1cb26e30-dd4e-456f-8ab4-beafd92e8f7a_b9831e7c-5ee2-48f0-87b7-26ae7c895158_62dc522e2b2d4e1398d1a56f1adad218_notes.pdf
|       |-- 1dd56fe1-6065-4bc2-86fc-131e5952f0bc_d90c3c44-ea84-418e-9ee3-172aabbe2220_1b771f42d62649a6a96c8b250dbb8096_notes.pdf
|       |-- 226b9756-3782-4127-b6c5-42543f983d57_ba01f853-e906-484d-867a-97f8c0d4a689_50ee734be0ef456bb220b430b8e103eb_notes.pdf
|       |-- 286d7e3a-52e2-47b7-913f-9196f7ddffcc_adcb90d1-ffbc-4dcb-ac3e-b35ad3acfb16_93bc6eb791c0455ca8e5b246e28c1832_notes.pdf
|       |-- 2b19a85e-b849-4ae0-8720-b5dffffeec73_d44b5e83-110d-4175-abe0-7dba941741da_5020aebc0e8b4c22bf5cee45d8886dd9_notes.pdf
|       |-- 2edc64bc-ba57-4a7d-ae8f-e3a084cb7ca5_74913aee-42eb-460e-940c-e9d620fb8e43_2d3e589af14142789cc32a341e94e0d2_notes.pdf
|       |-- 3031a588-432f-491d-812f-89dbd81c7479_7defedef-8b43-484a-9a4a-3753706ab5f1_29d2258494174acab16149f908bbdc5d_notes.pdf
|       |-- 31ed4b1f-3acb-4877-a66b-b8ddd3a3ec9a_3f791024-f20c-4eaa-a23f-02498e89c707_27991557a6264a188254970c4722708a_notes.pdf
|       |-- 34c2929f-ad86-4ca7-bf96-eebc0336eea8_5f702db0-ea7f-4c62-b657-8ad2c09ed6eb_46bc99c41bd2470f8a8da8efe7a74dfe_notes.pdf
|       |-- 3698d5ec-b7e4-4b0f-be8a-901bfe17f6b1_a13590ac-e578-46d3-9d04-75558dcdd3c3_e583329a0c704266b55cee5628739699_notes.pdf
|       |-- 36c9666c-3f0a-4b3b-9476-c6148d30fe5c_a38a0e51-df3c-454e-95d5-bc4bda162979_3cc14e37c34d4d828c9a0fca4173191f_notes.pdf
|       |-- 372c59d1-f9e1-4ae5-82fc-fc906d823ac3_d0920cda-a6c3-48eb-9bc2-ea218a638277_bf09dbaea41b4e87adeb6b43fd3be350_notes.pdf
|       |-- 3b7789c6-82e8-4b75-aabe-cc505accbeb9_89254927-15fd-4ba5-8d85-1d63043688fd_e37eded5cfa640a0862d0f6b364cd3da_notes.pdf
|       |-- 3c17a762-b910-4235-bfc6-d6c4d03bc2d4_d7ce6296-5444-489c-87e8-a01702b64804_7ed87875eaec4403b13d56a3b9e09691_notes.pdf
|       |-- 3c4849e3-b745-4e90-8109-f503f1eb5f0e_7656b39a-4285-45e3-a550-f1a2db9eed4d_648188c6246e4f678a2a48983f1108ac_notes.pdf
|       |-- 3c7dbe6a-39dd-4aee-b7a8-a49e9bfc2ba4_ecb0ccae-e960-4324-be1c-40cfaa04110c_f856b1e3b9ac4273972e3e3386a6d5e9_notes.pdf
|       |-- 3e1aa4c0-bd0b-4312-b139-0f81e4580e06_e3f8a840-20c9-4bbd-ad24-2e3654bd9d60_ca97fecccc8b4ffa8ae37781542f096c_notes.pdf
|       |-- 3e9f69f4-605e-4d05-9083-dcdff10179a7_fc62b74a-e83a-471f-978c-e1eadbad6f45_2eaa1e480bb640b982d36ad129e6878a_notes.pdf
|       |-- 3fc32e16-b26d-4f3b-8e85-f7c615fc0810_87b492a5-b949-4ece-8c3d-7d518730fb3a_1e7d2294f0e94a468677e00e4c6e4ae5_notes.pdf
|       |-- 4381be0b-b336-4b8b-92da-6b39be15dd69_e404e3d2-3dd5-4e81-8d75-a092ef5e6789_bcdb444ee2894380b0195a0d243b7814_notes.pdf
|       |-- 439b462b-46ee-4177-a82e-1a7818a4747c_608c8a5d-871e-43eb-8dee-ac3269f1ff96_40ab9f2f28ad49858b1cfe8529fab2b2_notes.pdf
|       |-- 44962fff-fbe4-4415-84a9-df5653999f5f_8ab2cf87-8cdc-40b3-9b6a-d065ca5bf46c_479c92f90e9c47cf959e120c86d02e01_notes.pdf
|       |-- 4c43c189-b582-4a04-ba2e-bf3396c47e04_db5680b3-aa51-4123-86ee-03d76a6310f3_34d817576a9748d9a791b7200db9345b_notes.pdf
|       |-- 4e057dc5-932d-4569-86eb-ad3b3cfecf40_98c5fc6e-ef00-4396-8073-9ebe0d0abbc1_24bfd7facba94351b62d64d0d357843d_notes.pdf
|       |-- 4f92d215-f511-4e6a-a503-6a8d3290f9af_99fb6f42-cc7f-4845-8464-56d70aedd9f8_e1149693dd984a698e83b95dcc05da07_notes.pdf
|       |-- 544c436c-8abe-4917-b6c2-f87446ed7218_e79c5257-fb5d-46c1-9f6e-a7096a7866c1_20b6088202aa43c0802a2007dde04b15_notes.pdf
|       |-- 56386e5c-ba7a-41dd-9ed0-b4eeb712c30c_4581e747-b86c-4c50-b1a8-03e8dc9e20bb_4395dbbea9884b0ebce8a17667e6465a_notes.pdf
|       |-- 593cc3df-0e39-490f-a53d-68fb4663739e_c6f6fe37-58b2-4c49-80cb-e4c8caaa7462_9090362d54024368b4e97bb0884522d2_notes.pdf
|       |-- 5c2666d1-c073-4176-bb99-b4f777b4e2e8_027055db-794b-4473-9718-af6b60190b68_d34232622b4b4e65b5fb56a2a60e2864_notes.pdf
|       |-- 5e394c65-b5ed-4c84-b85c-2504c8a93e1e_0cb1ba08-3699-4522-9f8d-36f0ee384475_ca6c22520add444aa642c6b9149c165f_notes.pdf
|       |-- 5ef88b13-8402-4da4-9df8-fac1f1e2bba0_382be5a4-2acd-428b-84ad-4c351560d0cd_ec18fb66788c4700a400d6061837f04d_notes.pdf
|       |-- 623cd438-6fdf-4c2c-a317-d9459acd309c_145fdceb-b3dd-462a-8056-f5a5bca07c70_67cacef24c9b4879ba81d488db16c206_notes.pdf
|       |-- 63040744-8810-41b2-b8ef-ffbd6c2f7825_d7bf5acc-7e0c-48bf-823f-3e483d61e837_7f528efe15e14c3aa7a1abd40e316de4_notes.pdf
|       |-- 63c4069e-989e-4f77-b661-9b077b4afa8b_be6473f0-ad2e-46fa-b9da-7415aee6187b_9937f041a5844daa82e908dc68dbdb6d_notes.pdf
|       |-- 6477f81a-14ed-4a6a-ae5a-ea45ae170be8_c9cdd503-5181-4060-89fc-cb3671b6b580_04df9a5bd1a448c48c7e992a54dad63e_notes.pdf
|       |-- 648210d2-21d2-47e1-98fe-7067c74727bd_8d17d6f1-0390-429c-aa1e-7bafe7ebcfa3_774e388b229d4c9da02104450cc01e92_notes.pdf
|       |-- 664b5e0c-400a-4f5a-b74a-889b3943e288_a73b138e-4354-4ffc-be66-c02bd0cce470_86e42c767c0c41ed92cf9ff434e2f023_notes.pdf
|       |-- 6a71c530-1175-4253-b767-3856b5328388_eb9c0413-b9ac-40ba-8c2f-bff5ff93b9db_f67306a4152c424ebac5f03229642d77_notes.pdf
|       |-- 6d3b21ff-c291-41f6-9b36-3cf382ae1ba4_92b9a779-efe4-4bfc-af02-c99a362b05aa_051cb6c20e60481a8c838fa4ab9727f6_notes.pdf
|       |-- 6e5fbd8b-9d41-4e56-8ea1-6cdfd376361d_cef4e50d-6a52-491d-949e-655026d9b7a6_63199984ac504bafa1ab4a763c081d9d_notes.pdf
|       |-- 728e0868-e390-4b25-9ff8-ac7597543db7_850b58e0-7c1f-4652-b144-811c406eba09_f5fcb1dfcd174d3cb7d9f22488d18385_notes.pdf
|       |-- 74346356-6b8e-4b6a-ad05-ed2d1bf876cd_f0ba66af-7aac-47ce-8c29-de3b220eb401_aa028ef085f1417e8d7c1ffc88015a13_notes.pdf
|       |-- 74e933b5-f407-4e0a-8a8c-e768cf56a03a_e5a6781c-8048-4b6c-a393-b794cfe8f055_c6f65484018448e9af7217ab08e5c9be_notes.pdf
|       |-- 7747b313-d2a7-4971-a96d-fe36e3a9419f_fef95337-478f-41e8-a230-651bccfcc11b_503247b2dee24dc5ad6d6af9a2c1e0e3_notes.pdf
|       |-- 79ac1206-6d65-4d71-83b5-b48f0f5ddedf_eabd492f-eefe-455c-bc61-09812963296b_a405505779c848fd94d6fb4cf0447e1b_notes.pdf
|       |-- 7a9abb13-e938-488c-9f92-254fc01ca647_45da9b86-0abb-4cf2-b498-3a637888f11d_43f397ceb6ec42bdb739e81630adf742_notes.pdf
|       |-- 7e568892-5574-4de9-8448-0c84bbd2a002_35bb42cc-4d32-4ca5-b956-0a0ef0a116ec_8109889f8f4e4842a4f51b5afe1539d2_notes.pdf
|       |-- 7eee23a5-3f01-4ae6-9da4-2e591382e656_0057a0a3-1481-446e-8e8f-52592c712274_265d538713db486eb4c88cf037052529_notes.pdf
|       |-- 83ee5eb3-1228-47a5-b76e-0b2d3a558cb5_5aea2d21-2d6e-4ba1-afed-2588b31b6880_3f72911af11e4209acdd53282ea17881_notes.pdf
|       |-- 882cda48-2cd0-4ace-84f4-f414892caf55_066f8e51-58a4-4fdc-abc4-6b076e7f7a8a_c759cbd907e5459891714be7174596fa_notes.pdf
|       |-- 885f8ebd-4d99-4cd3-9b47-3a2282affbbf_23cf65b4-54d2-4d7a-8fef-7e572c2eb5af_15f26a98db58416f98c511be9f801ea3_notes.pdf
|       |-- 9299bb99-4ccc-4dc9-81f3-c65cdd1841b7_2f1a1bf0-cd39-4add-a51d-187361788f4f_254f22e506774267a152013d030df014_notes.pdf
|       |-- 944049d9-e851-4e32-a500-1965aec2b018_3a02076e-513e-44d1-9907-a46b4fb1a6ce_e72c4487bc444fb6a03e807f691f7c34_notes.pdf
|       |-- 94432bbd-3bfd-4aec-b4a5-22b946786112_b0a760c9-7d83-477f-b9c4-f6d25b3f2a58_ab076564bf4842c1b27a9ca447d67eca_notes.pdf
|       |-- 94bb0f17-00e4-48b0-853a-04469ff9dd62_8436d50b-9edf-4fdc-ae95-dbe3654eea19_68583f376a2a4ea8a6296330e9dd9a10_notes.pdf
|       |-- 963e4d06-dac4-406c-bd8d-530f2dae7e57_bc5c63db-169f-485b-a67b-54c5635d4e14_3d4b4e6f46fa45efb1d95dcc6ec45385_notes.pdf
|       |-- 98bd527d-14af-4cb4-a3fe-5e8a0788f6e6_7d82e584-c790-43f3-a095-26f582b29b55_b72e814bcc8f4a489ce699c47ee63801_notes.pdf
|       |-- 9ab6cd24-c27b-4c1f-b49a-07820472e57a_a315272d-c702-440d-b833-c8dd8cc109ae_7e440ee4fec7409a8efecb73daad0fbd_notes.pdf
|       |-- 9dd77bc2-a3f4-4105-b1c7-408076b69e2b_43adc7d1-ff7d-4d4e-a1c3-89f1321665b2_b8429998421949f5a94d5b9916ebec7f_notes.pdf
|       |-- 9f2f5b10-9173-45a3-9947-7b8b8f24d3ce_f99cff2a-41bb-4521-bdb1-aa19bc2db58d_80dc0d609b5142cc8ad553d795a5b33b_notes.pdf
|       |-- a0a30e3d-4d28-4975-bda8-9f06e18d4965_ee977088-7c76-4f9c-8c5d-950176ddd767_640df4be3a604c10b4424a3048698edb_notes.pdf
|       |-- a3899a8d-cc52-4dc7-a551-1e90cd096cac_52d6f499-67e4-45f0-9343-c8d4761e6da5_fe27b47f61594550924aab08d3d80fb8_notes.pdf
|       |-- a39e3654-cdf0-47d7-849b-ab1cf54881e7_c8811a3a-fbec-4634-b034-744ce5aaf6e0_650c5db19a5746ac9f134bdf8873da02_notes.pdf
|       |-- a84739f0-6a79-4a2a-a2c6-2e1cf0c39c40_035147e9-314c-43f9-a5ff-616c8b17a981_ccab2773590047b4bb5383d361fa40e1_notes.pdf
|       |-- aa72c3a3-ab0b-4ad1-bd1b-27a2f69bdc40_b0b7c726-5735-479e-8fa2-e6f49e79a994_8a990f1bab4e4a18883ff6d64ff0912e_notes.pdf
|       |-- ac0ca3a1-1aea-4567-b974-6c8685e3a3b9_3290f9bd-69cd-4741-9f1a-3993e5cd1c74_136ce7d3a1cd4228b578dd7c74bfa716_notes.pdf
|       |-- ac90b7b8-9b32-414c-8364-085cd0513420_ed4d0be3-a7f4-43fa-bf66-d4bfeb4abfa1_52912261cc1f42ed99b39850bf5cc7d3_notes.pdf
|       |-- ae7ad781-d52d-428e-bd8c-cb291d5a2f4e_91ac5f9b-9f79-4360-ae5c-b39a62bea814_d81a0395e6e64bbe95f8774a50d3a1a4_notes.pdf
|       |-- b0d8acbc-fe23-48e0-8d3a-81683a51c90f_4c139ce4-7c9c-4e35-a784-9d2817eefacb_f2250df8c80c464590db48510e3a6d8e_notes.pdf
|       |-- b10f4d20-5de8-4cf1-a85f-5e59d9bedcbc_73306fb8-ca7b-4737-bf76-dd2ede520c29_a27dca8280bf4ba1af962fdd1ed6a5f0_notes.pdf
|       |-- b5b68109-8578-4912-89e5-36b8a622feaf_cca01670-5a97-4744-9933-700346c9e363_898e3110878f411d8b5d829304215cc4_notes.pdf
|       |-- b7dfb360-d17e-489e-a20a-07561c1f29e2_a45473c2-a807-4d9a-bf5e-7640d122b417_35d122bcff9349d39db12fbd453e3e49_notes.pdf
|       |-- b7f9869e-9af7-4047-879c-0a64ac8f371b_a9563251-bf16-4a2c-a733-3ad12e288ba7_1016ddc3711f4d5199fc31824667f766_notes.pdf
|       |-- b802b450-5790-4a46-9984-fd3cbf82eb49_6cf25b2d-81d0-4847-9faa-783334af0211_1fbddd1de97b4143be892734c9b7acf0_notes.pdf
|       |-- b8cfaff3-4360-4907-aaa7-f159d8f5f15a_37468e2a-db63-49f7-8b8d-733e94d1fa1a_c2a187246c844ff59920bec52e09904f_notes.pdf
|       |-- bd79d089-f41d-4389-8cc9-350f34c0403b_6f5de6cc-b1dd-4c8f-bdeb-50289795ff29_543c5456c07b43639b74cd8e91e6246a_notes.pdf
|       |-- c289881e-31f0-4fe6-a180-9c435846590e_43e77a74-a43e-4021-b1ae-0981329facb7_9effda6740aa46f5b3cf5f85038483bd_notes.pdf
|       |-- c441e296-5326-4851-8b13-ef225830ac7a_fe5bf53c-6b08-4b0d-9e5b-75965b5590ae_0850b24b93a940489caeb564f201487a_notes.pdf
|       |-- c8b496bd-fedc-4982-8f56-3166f928c2bf_4751f582-9c44-480a-8f3b-b35c342843aa_e8c4439a2856460c997946e54edc5236_notes.pdf
|       |-- cb339136-5d34-4f47-82a5-fa174bcbcc60_57d63676-b371-4add-bb9a-14541136235e_3826942c9162483d89a458f6d3122ea3_notes.pdf
|       |-- cb62cac9-8ffa-4a7b-a147-1d1e8c26aa93_16b39361-9a15-41cc-bb25-0b66d3178391_0fa5ad9275e6484e87973e2f2d23b8ad_notes.pdf
|       |-- d50ce666-f388-4c8c-8f19-1e764e017d84_7af8fae2-338e-4cca-9f0c-bbf43176152c_81d8d6cca2914215a17660574b056c9a_notes.pdf
|       |-- df5e9aa3-d52b-42c5-aeb9-e57f54e3b4fa_01717679-3bcc-4814-b757-0f185a87c42c_5ff96a5aac374c19a45ebf0ec7144591_notes.pdf
|       |-- e063ef6c-b8f9-4669-8da1-78e9d56e82a5_17470ecb-3c2a-4200-a00b-94463f5266b9_deaeedec070b42d4a49153aec797438c_notes.pdf
|       |-- e387e57d-7158-4e75-9bff-1d880b86582a_bf0fbddf-449c-47a5-9b5d-b681ecbb0108_4e6b567dff2f4d4d95bcb69751d8ad2a_notes.pdf
|       |-- e9fe5853-ad7f-482e-ad77-9f288bc60092_70086cf7-1629-49f5-bba1-94fdf1d89b1a_60b833a81e4349a4a8bedb286c987d52_notes.pdf
|       |-- ea13d002-f19f-4fd8-bfc8-befe0f2d2a25_1298813a-4d6b-4138-b27a-e094784e9e0b_596f03e7a8d64ec6b075a465a4736952_notes.pdf
|       |-- ecf2a011-76ff-4bf1-bb92-8a8d52e96327_dabf3994-603e-4e45-a1ed-43201a4d8b2c_7491f2d28bab4d85a0535b1f2d72a14e_notes.pdf
|       \-- ff7d1190-90fd-4272-b5ec-bd217aaab30f_9b893b5b-765b-449e-a949-fad29b5d5ffa_8d39c858f0fa4806a4505370832d3e09_notes.pdf
|-- raw
|   |-- Admin Review Dashboard.md for AIaaS.txt
|   |-- Below is a production-grade AI Engi.txt
|   |-- Below is a production-grade Archite.txt
|   |-- Below is a production-grade Databas.txt
|   |-- Below is a production-grade Filteri.txt
|   |-- Below is a production-grade Hosting.txt
|   |-- Below is a production-grade System.txt
|   |-- Below is a production-grade Tech St.txt
|   |-- Below is a production-grade UI Desi.txt
|   |-- Security Checks.md for AIaaS..txt
|   \-- Sitemap & Wireframe.md for AIaaS..txt
|-- repo
|   |-- langchain
|   |   |-- .devcontainer
|   |   |   |-- devcontainer.json
|   |   |   |-- docker-compose.yaml
|   |   |   \-- README.md
|   |   |-- .github
|   |   |   |-- actions
|   |   |   |   \-- uv_setup
|   |   |   |       \-- action.yml
|   |   |   |-- images
|   |   |   |   |-- logo-dark.svg
|   |   |   |   \-- logo-light.svg
|   |   |   |-- ISSUE_TEMPLATE
|   |   |   |   |-- bug-report.yml
|   |   |   |   |-- config.yml
|   |   |   |   |-- feature-request.yml
|   |   |   |   |-- privileged.yml
|   |   |   |   \-- task.yml
|   |   |   |-- scripts
|   |   |   |   |-- check_diff.py
|   |   |   |   |-- check_prerelease_dependencies.py
|   |   |   |   \-- get_min_versions.py
|   |   |   |-- tools
|   |   |   |   \-- git-restore-mtime
|   |   |   |-- workflows
|   |   |   |   |-- _compile_integration_test.yml
|   |   |   |   |-- _lint.yml
|   |   |   |   |-- _release.yml
|   |   |   |   |-- _test.yml
|   |   |   |   |-- _test_pydantic.yml
|   |   |   |   |-- auto-label-by-package.yml
|   |   |   |   |-- check_agents_sync.yml
|   |   |   |   |-- check_core_versions.yml
|   |   |   |   |-- check_diffs.yml
|   |   |   |   |-- integration_tests.yml
|   |   |   |   |-- pr_labeler_file.yml
|   |   |   |   |-- pr_labeler_title.yml
|   |   |   |   |-- pr_lint.yml
|   |   |   |   |-- refresh_model_profiles.yml
|   |   |   |   |-- tag-external-contributions.yml
|   |   |   |   \-- v03_api_doc_build.yml
|   |   |   |-- CODEOWNERS
|   |   |   |-- dependabot.yml
|   |   |   |-- pr-file-labeler.yml
|   |   |   \-- PULL_REQUEST_TEMPLATE.md
|   |   |-- .vscode
|   |   |   |-- extensions.json
|   |   |   \-- settings.json
|   |   |-- libs
|   |   |   |-- core
|   |   |   |   |-- langchain_core
|   |   |   |   |   |-- _api
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- beta_decorator.py
|   |   |   |   |   |   |-- deprecation.py
|   |   |   |   |   |   |-- internal.py
|   |   |   |   |   |   \-- path.py
|   |   |   |   |   |-- _security
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- _ssrf_protection.py
|   |   |   |   |   |-- callbacks
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |-- file.py
|   |   |   |   |   |   |-- manager.py
|   |   |   |   |   |   |-- stdout.py
|   |   |   |   |   |   |-- streaming_stdout.py
|   |   |   |   |   |   \-- usage.py
|   |   |   |   |   |-- document_loaders
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |-- blob_loaders.py
|   |   |   |   |   |   \-- langsmith.py
|   |   |   |   |   |-- documents
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |-- compressor.py
|   |   |   |   |   |   \-- transformers.py
|   |   |   |   |   |-- embeddings
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- embeddings.py
|   |   |   |   |   |   \-- fake.py
|   |   |   |   |   |-- example_selectors
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |-- length_based.py
|   |   |   |   |   |   \-- semantic_similarity.py
|   |   |   |   |   |-- indexing
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- api.py
|   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   \-- in_memory.py
|   |   |   |   |   |-- language_models
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- _utils.py
|   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |-- chat_models.py
|   |   |   |   |   |   |-- fake.py
|   |   |   |   |   |   |-- fake_chat_models.py
|   |   |   |   |   |   |-- llms.py
|   |   |   |   |   |   \-- model_profile.py
|   |   |   |   |   |-- load
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- _validation.py
|   |   |   |   |   |   |-- dump.py
|   |   |   |   |   |   |-- load.py
|   |   |   |   |   |   |-- mapping.py
|   |   |   |   |   |   \-- serializable.py
|   |   |   |   |   |-- messages
|   |   |   |   |   |   |-- block_translators
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- anthropic.py
|   |   |   |   |   |   |   |-- bedrock.py
|   |   |   |   |   |   |   |-- bedrock_converse.py
|   |   |   |   |   |   |   |-- google_genai.py
|   |   |   |   |   |   |   |-- google_vertexai.py
|   |   |   |   |   |   |   |-- groq.py
|   |   |   |   |   |   |   |-- langchain_v0.py
|   |   |   |   |   |   |   \-- openai.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- ai.py
|   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |-- chat.py
|   |   |   |   |   |   |-- content.py
|   |   |   |   |   |   |-- function.py
|   |   |   |   |   |   |-- human.py
|   |   |   |   |   |   |-- modifier.py
|   |   |   |   |   |   |-- system.py
|   |   |   |   |   |   |-- tool.py
|   |   |   |   |   |   \-- utils.py
|   |   |   |   |   |-- output_parsers
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |-- format_instructions.py
|   |   |   |   |   |   |-- json.py
|   |   |   |   |   |   |-- list.py
|   |   |   |   |   |   |-- openai_functions.py
|   |   |   |   |   |   |-- openai_tools.py
|   |   |   |   |   |   |-- pydantic.py
|   |   |   |   |   |   |-- string.py
|   |   |   |   |   |   |-- transform.py
|   |   |   |   |   |   \-- xml.py
|   |   |   |   |   |-- outputs
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- chat_generation.py
|   |   |   |   |   |   |-- chat_result.py
|   |   |   |   |   |   |-- generation.py
|   |   |   |   |   |   |-- llm_result.py
|   |   |   |   |   |   \-- run_info.py
|   |   |   |   |   |-- prompts
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |-- chat.py
|   |   |   |   |   |   |-- dict.py
|   |   |   |   |   |   |-- few_shot.py
|   |   |   |   |   |   |-- few_shot_with_templates.py
|   |   |   |   |   |   |-- image.py
|   |   |   |   |   |   |-- loading.py
|   |   |   |   |   |   |-- message.py
|   |   |   |   |   |   |-- prompt.py
|   |   |   |   |   |   |-- string.py
|   |   |   |   |   |   \-- structured.py
|   |   |   |   |   |-- runnables
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |-- branch.py
|   |   |   |   |   |   |-- config.py
|   |   |   |   |   |   |-- configurable.py
|   |   |   |   |   |   |-- fallbacks.py
|   |   |   |   |   |   |-- graph.py
|   |   |   |   |   |   |-- graph_ascii.py
|   |   |   |   |   |   |-- graph_mermaid.py
|   |   |   |   |   |   |-- graph_png.py
|   |   |   |   |   |   |-- history.py
|   |   |   |   |   |   |-- passthrough.py
|   |   |   |   |   |   |-- retry.py
|   |   |   |   |   |   |-- router.py
|   |   |   |   |   |   |-- schema.py
|   |   |   |   |   |   \-- utils.py
|   |   |   |   |   |-- tools
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |-- convert.py
|   |   |   |   |   |   |-- render.py
|   |   |   |   |   |   |-- retriever.py
|   |   |   |   |   |   |-- simple.py
|   |   |   |   |   |   \-- structured.py
|   |   |   |   |   |-- tracers
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- _compat.py
|   |   |   |   |   |   |-- _streaming.py
|   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |-- context.py
|   |   |   |   |   |   |-- core.py
|   |   |   |   |   |   |-- evaluation.py
|   |   |   |   |   |   |-- event_stream.py
|   |   |   |   |   |   |-- langchain.py
|   |   |   |   |   |   |-- log_stream.py
|   |   |   |   |   |   |-- memory_stream.py
|   |   |   |   |   |   |-- root_listeners.py
|   |   |   |   |   |   |-- run_collector.py
|   |   |   |   |   |   |-- schemas.py
|   |   |   |   |   |   \-- stdout.py
|   |   |   |   |   |-- utils
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- _merge.py
|   |   |   |   |   |   |-- aiter.py
|   |   |   |   |   |   |-- env.py
|   |   |   |   |   |   |-- formatting.py
|   |   |   |   |   |   |-- function_calling.py
|   |   |   |   |   |   |-- html.py
|   |   |   |   |   |   |-- image.py
|   |   |   |   |   |   |-- input.py
|   |   |   |   |   |   |-- interactive_env.py
|   |   |   |   |   |   |-- iter.py
|   |   |   |   |   |   |-- json.py
|   |   |   |   |   |   |-- json_schema.py
|   |   |   |   |   |   |-- mustache.py
|   |   |   |   |   |   |-- pydantic.py
|   |   |   |   |   |   |-- strings.py
|   |   |   |   |   |   |-- usage.py
|   |   |   |   |   |   |-- utils.py
|   |   |   |   |   |   \-- uuid.py
|   |   |   |   |   |-- vectorstores
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |-- in_memory.py
|   |   |   |   |   |   \-- utils.py
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- _import_utils.py
|   |   |   |   |   |-- agents.py
|   |   |   |   |   |-- caches.py
|   |   |   |   |   |-- chat_history.py
|   |   |   |   |   |-- chat_loaders.py
|   |   |   |   |   |-- chat_sessions.py
|   |   |   |   |   |-- env.py
|   |   |   |   |   |-- exceptions.py
|   |   |   |   |   |-- globals.py
|   |   |   |   |   |-- prompt_values.py
|   |   |   |   |   |-- py.typed
|   |   |   |   |   |-- rate_limiters.py
|   |   |   |   |   |-- retrievers.py
|   |   |   |   |   |-- stores.py
|   |   |   |   |   |-- structured_query.py
|   |   |   |   |   |-- sys_info.py
|   |   |   |   |   \-- version.py
|   |   |   |   |-- scripts
|   |   |   |   |   |-- check_imports.py
|   |   |   |   |   |-- check_version.py
|   |   |   |   |   \-- lint_imports.sh
|   |   |   |   |-- tests
|   |   |   |   |   |-- benchmarks
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_async_callbacks.py
|   |   |   |   |   |   \-- test_imports.py
|   |   |   |   |   |-- integration_tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_compile.py
|   |   |   |   |   |-- unit_tests
|   |   |   |   |   |   |-- _api
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_beta_decorator.py
|   |   |   |   |   |   |   |-- test_deprecation.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   \-- test_path.py
|   |   |   |   |   |   |-- caches
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_in_memory_cache.py
|   |   |   |   |   |   |-- callbacks
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_async_callback_manager.py
|   |   |   |   |   |   |   |-- test_dispatch_custom_event.py
|   |   |   |   |   |   |   |-- test_handle_event.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   |-- test_sync_callback_manager.py
|   |   |   |   |   |   |   \-- test_usage_callback.py
|   |   |   |   |   |   |-- chat_history
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_chat_history.py
|   |   |   |   |   |   |-- data
|   |   |   |   |   |   |   |-- prompts
|   |   |   |   |   |   |   |   |-- prompt_extra_args.json
|   |   |   |   |   |   |   |   |-- prompt_missing_args.json
|   |   |   |   |   |   |   |   \-- simple_prompt.json
|   |   |   |   |   |   |   \-- prompt_file.txt
|   |   |   |   |   |   |-- dependencies
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_dependencies.py
|   |   |   |   |   |   |-- document_loaders
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_base.py
|   |   |   |   |   |   |   \-- test_langsmith.py
|   |   |   |   |   |   |-- documents
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_document.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   \-- test_str.py
|   |   |   |   |   |   |-- embeddings
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_deterministic_embedding.py
|   |   |   |   |   |   |-- example_selectors
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_base.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   |-- test_length_based_example_selector.py
|   |   |   |   |   |   |   \-- test_similarity.py
|   |   |   |   |   |   |-- examples
|   |   |   |   |   |   |   |-- example-non-utf8.csv
|   |   |   |   |   |   |   |-- example-non-utf8.txt
|   |   |   |   |   |   |   |-- example-utf8.csv
|   |   |   |   |   |   |   |-- example-utf8.txt
|   |   |   |   |   |   |   |-- example_prompt.json
|   |   |   |   |   |   |   |-- examples.json
|   |   |   |   |   |   |   |-- examples.yaml
|   |   |   |   |   |   |   |-- few_shot_prompt.json
|   |   |   |   |   |   |   |-- few_shot_prompt.yaml
|   |   |   |   |   |   |   |-- few_shot_prompt_example_prompt.json
|   |   |   |   |   |   |   |-- few_shot_prompt_examples_in.json
|   |   |   |   |   |   |   |-- few_shot_prompt_yaml_examples.yaml
|   |   |   |   |   |   |   |-- jinja_injection_prompt.json
|   |   |   |   |   |   |   |-- jinja_injection_prompt.yaml
|   |   |   |   |   |   |   |-- prompt_with_output_parser.json
|   |   |   |   |   |   |   |-- simple_prompt.json
|   |   |   |   |   |   |   |-- simple_prompt.yaml
|   |   |   |   |   |   |   |-- simple_prompt_with_template_file.json
|   |   |   |   |   |   |   \-- simple_template.txt
|   |   |   |   |   |   |-- fake
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- callbacks.py
|   |   |   |   |   |   |   \-- test_fake_chat_model.py
|   |   |   |   |   |   |-- indexing
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_hashed_document.py
|   |   |   |   |   |   |   |-- test_in_memory_indexer.py
|   |   |   |   |   |   |   |-- test_in_memory_record_manager.py
|   |   |   |   |   |   |   |-- test_indexing.py
|   |   |   |   |   |   |   \-- test_public_api.py
|   |   |   |   |   |   |-- language_models
|   |   |   |   |   |   |   |-- chat_models
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- test_base.py
|   |   |   |   |   |   |   |   |-- test_benchmark.py
|   |   |   |   |   |   |   |   |-- test_cache.py
|   |   |   |   |   |   |   |   \-- test_rate_limiting.py
|   |   |   |   |   |   |   |-- llms
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- test_base.py
|   |   |   |   |   |   |   |   \-- test_cache.py
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_imports.py
|   |   |   |   |   |   |-- load
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   |-- test_secret_injection.py
|   |   |   |   |   |   |   \-- test_serializable.py
|   |   |   |   |   |   |-- messages
|   |   |   |   |   |   |   |-- block_translators
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- test_anthropic.py
|   |   |   |   |   |   |   |   |-- test_bedrock.py
|   |   |   |   |   |   |   |   |-- test_bedrock_converse.py
|   |   |   |   |   |   |   |   |-- test_google_genai.py
|   |   |   |   |   |   |   |   |-- test_groq.py
|   |   |   |   |   |   |   |   |-- test_langchain_v0.py
|   |   |   |   |   |   |   |   |-- test_openai.py
|   |   |   |   |   |   |   |   \-- test_registration.py
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_ai.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   \-- test_utils.py
|   |   |   |   |   |   |-- output_parsers
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_base_parsers.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   |-- test_json.py
|   |   |   |   |   |   |   |-- test_list_parser.py
|   |   |   |   |   |   |   |-- test_openai_functions.py
|   |   |   |   |   |   |   |-- test_openai_tools.py
|   |   |   |   |   |   |   |-- test_pydantic_parser.py
|   |   |   |   |   |   |   \-- test_xml_parser.py
|   |   |   |   |   |   |-- outputs
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_chat_generation.py
|   |   |   |   |   |   |   \-- test_imports.py
|   |   |   |   |   |   |-- prompts
|   |   |   |   |   |   |   |-- __snapshots__
|   |   |   |   |   |   |   |   |-- test_chat.ambr
|   |   |   |   |   |   |   |   \-- test_prompt.ambr
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- prompt_extra_args.json
|   |   |   |   |   |   |   |-- prompt_missing_args.json
|   |   |   |   |   |   |   |-- simple_prompt.json
|   |   |   |   |   |   |   |-- test_chat.py
|   |   |   |   |   |   |   |-- test_dict.py
|   |   |   |   |   |   |   |-- test_few_shot.py
|   |   |   |   |   |   |   |-- test_few_shot_with_templates.py
|   |   |   |   |   |   |   |-- test_image.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   |-- test_loading.py
|   |   |   |   |   |   |   |-- test_prompt.py
|   |   |   |   |   |   |   |-- test_string.py
|   |   |   |   |   |   |   |-- test_structured.py
|   |   |   |   |   |   |   \-- test_utils.py
|   |   |   |   |   |   |-- rate_limiters
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_in_memory_rate_limiter.py
|   |   |   |   |   |   |-- runnables
|   |   |   |   |   |   |   |-- __snapshots__
|   |   |   |   |   |   |   |   |-- test_fallbacks.ambr
|   |   |   |   |   |   |   |   |-- test_graph.ambr
|   |   |   |   |   |   |   |   \-- test_runnable.ambr
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_concurrency.py
|   |   |   |   |   |   |   |-- test_config.py
|   |   |   |   |   |   |   |-- test_configurable.py
|   |   |   |   |   |   |   |-- test_fallbacks.py
|   |   |   |   |   |   |   |-- test_graph.py
|   |   |   |   |   |   |   |-- test_history.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   |-- test_runnable.py
|   |   |   |   |   |   |   |-- test_runnable_events_v1.py
|   |   |   |   |   |   |   |-- test_runnable_events_v2.py
|   |   |   |   |   |   |   |-- test_tracing_interops.py
|   |   |   |   |   |   |   \-- test_utils.py
|   |   |   |   |   |   |-- stores
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_in_memory.py
|   |   |   |   |   |   |-- tracers
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_async_base_tracer.py
|   |   |   |   |   |   |   |-- test_automatic_metadata.py
|   |   |   |   |   |   |   |-- test_base_tracer.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   |-- test_langchain.py
|   |   |   |   |   |   |   |-- test_memory_stream.py
|   |   |   |   |   |   |   |-- test_run_collector.py
|   |   |   |   |   |   |   \-- test_schemas.py
|   |   |   |   |   |   |-- utils
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_aiter.py
|   |   |   |   |   |   |   |-- test_env.py
|   |   |   |   |   |   |   |-- test_formatting.py
|   |   |   |   |   |   |   |-- test_function_calling.py
|   |   |   |   |   |   |   |-- test_html.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   |-- test_iter.py
|   |   |   |   |   |   |   |-- test_json_schema.py
|   |   |   |   |   |   |   |-- test_pydantic.py
|   |   |   |   |   |   |   |-- test_rm_titles.py
|   |   |   |   |   |   |   |-- test_strings.py
|   |   |   |   |   |   |   |-- test_usage.py
|   |   |   |   |   |   |   |-- test_utils.py
|   |   |   |   |   |   |   \-- test_uuid_utils.py
|   |   |   |   |   |   |-- vectorstores
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_in_memory.py
|   |   |   |   |   |   |   |-- test_utils.py
|   |   |   |   |   |   |   \-- test_vectorstore.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- prompt_file.txt
|   |   |   |   |   |   |-- pydantic_utils.py
|   |   |   |   |   |   |-- stubs.py
|   |   |   |   |   |   |-- test_globals.py
|   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |-- test_messages.py
|   |   |   |   |   |   |-- test_outputs.py
|   |   |   |   |   |   |-- test_prompt_values.py
|   |   |   |   |   |   |-- test_pydantic_imports.py
|   |   |   |   |   |   |-- test_pydantic_serde.py
|   |   |   |   |   |   |-- test_retrievers.py
|   |   |   |   |   |   |-- test_setup.py
|   |   |   |   |   |   |-- test_ssrf_protection.py
|   |   |   |   |   |   |-- test_sys_info.py
|   |   |   |   |   |   \-- test_tools.py
|   |   |   |   |   \-- __init__.py
|   |   |   |   |-- extended_testing_deps.txt
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   \-- uv.lock
|   |   |   |-- langchain
|   |   |   |   |-- langchain_classic
|   |   |   |   |   |-- _api
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- deprecation.py
|   |   |   |   |   |   |-- interactive_env.py
|   |   |   |   |   |   |-- module_import.py
|   |   |   |   |   |   \-- path.py
|   |   |   |   |   |-- adapters
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- openai.py
|   |   |   |   |   |-- agents
|   |   |   |   |   |   |-- agent_toolkits
|   |   |   |   |   |   |   |-- ainetwork
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- toolkit.py
|   |   |   |   |   |   |   |-- amadeus
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- toolkit.py
|   |   |   |   |   |   |   |-- clickup
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- toolkit.py
|   |   |   |   |   |   |   |-- conversational_retrieval
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- openai_functions.py
|   |   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |   |-- csv
|   |   |   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |   |   |-- file_management
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- toolkit.py
|   |   |   |   |   |   |   |-- github
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- toolkit.py
|   |   |   |   |   |   |   |-- gitlab
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- toolkit.py
|   |   |   |   |   |   |   |-- gmail
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- toolkit.py
|   |   |   |   |   |   |   |-- jira
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- toolkit.py
|   |   |   |   |   |   |   |-- json
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |   |-- prompt.py
|   |   |   |   |   |   |   |   \-- toolkit.py
|   |   |   |   |   |   |   |-- multion
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- toolkit.py
|   |   |   |   |   |   |   |-- nasa
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- toolkit.py
|   |   |   |   |   |   |   |-- nla
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- tool.py
|   |   |   |   |   |   |   |   \-- toolkit.py
|   |   |   |   |   |   |   |-- office365
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- toolkit.py
|   |   |   |   |   |   |   |-- openapi
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |   |-- planner.py
|   |   |   |   |   |   |   |   |-- planner_prompt.py
|   |   |   |   |   |   |   |   |-- prompt.py
|   |   |   |   |   |   |   |   |-- spec.py
|   |   |   |   |   |   |   |   \-- toolkit.py
|   |   |   |   |   |   |   |-- pandas
|   |   |   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |   |   |-- playwright
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- toolkit.py
|   |   |   |   |   |   |   |-- powerbi
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |   |-- chat_base.py
|   |   |   |   |   |   |   |   |-- prompt.py
|   |   |   |   |   |   |   |   \-- toolkit.py
|   |   |   |   |   |   |   |-- python
|   |   |   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |   |   |-- slack
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- toolkit.py
|   |   |   |   |   |   |   |-- spark
|   |   |   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |   |   |-- spark_sql
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |   |-- prompt.py
|   |   |   |   |   |   |   |   \-- toolkit.py
|   |   |   |   |   |   |   |-- sql
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |   |-- prompt.py
|   |   |   |   |   |   |   |   \-- toolkit.py
|   |   |   |   |   |   |   |-- steam
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- toolkit.py
|   |   |   |   |   |   |   |-- vectorstore
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |   |-- prompt.py
|   |   |   |   |   |   |   |   \-- toolkit.py
|   |   |   |   |   |   |   |-- xorbits
|   |   |   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |   |   |-- zapier
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- toolkit.py
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- azure_cognitive_services.py
|   |   |   |   |   |   |   \-- base.py
|   |   |   |   |   |   |-- chat
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- output_parser.py
|   |   |   |   |   |   |   \-- prompt.py
|   |   |   |   |   |   |-- conversational
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- output_parser.py
|   |   |   |   |   |   |   \-- prompt.py
|   |   |   |   |   |   |-- conversational_chat
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- output_parser.py
|   |   |   |   |   |   |   \-- prompt.py
|   |   |   |   |   |   |-- format_scratchpad
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- log.py
|   |   |   |   |   |   |   |-- log_to_messages.py
|   |   |   |   |   |   |   |-- openai_functions.py
|   |   |   |   |   |   |   |-- openai_tools.py
|   |   |   |   |   |   |   |-- tools.py
|   |   |   |   |   |   |   \-- xml.py
|   |   |   |   |   |   |-- json_chat
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   \-- prompt.py
|   |   |   |   |   |   |-- mrkl
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- output_parser.py
|   |   |   |   |   |   |   \-- prompt.py
|   |   |   |   |   |   |-- openai_assistant
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- base.py
|   |   |   |   |   |   |-- openai_functions_agent
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- agent_token_buffer_memory.py
|   |   |   |   |   |   |   \-- base.py
|   |   |   |   |   |   |-- openai_functions_multi_agent
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- base.py
|   |   |   |   |   |   |-- openai_tools
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- base.py
|   |   |   |   |   |   |-- output_parsers
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- json.py
|   |   |   |   |   |   |   |-- openai_functions.py
|   |   |   |   |   |   |   |-- openai_tools.py
|   |   |   |   |   |   |   |-- react_json_single_input.py
|   |   |   |   |   |   |   |-- react_single_input.py
|   |   |   |   |   |   |   |-- self_ask.py
|   |   |   |   |   |   |   |-- tools.py
|   |   |   |   |   |   |   \-- xml.py
|   |   |   |   |   |   |-- react
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- agent.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- output_parser.py
|   |   |   |   |   |   |   |-- textworld_prompt.py
|   |   |   |   |   |   |   \-- wiki_prompt.py
|   |   |   |   |   |   |-- self_ask_with_search
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- output_parser.py
|   |   |   |   |   |   |   \-- prompt.py
|   |   |   |   |   |   |-- structured_chat
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- output_parser.py
|   |   |   |   |   |   |   \-- prompt.py
|   |   |   |   |   |   |-- tool_calling_agent
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- base.py
|   |   |   |   |   |   |-- xml
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   \-- prompt.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- agent.py
|   |   |   |   |   |   |-- agent_iterator.py
|   |   |   |   |   |   |-- agent_types.py
|   |   |   |   |   |   |-- initialize.py
|   |   |   |   |   |   |-- load_tools.py
|   |   |   |   |   |   |-- loading.py
|   |   |   |   |   |   |-- schema.py
|   |   |   |   |   |   |-- tools.py
|   |   |   |   |   |   |-- types.py
|   |   |   |   |   |   \-- utils.py
|   |   |   |   |   |-- callbacks
|   |   |   |   |   |   |-- streamlit
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- mutable_expander.py
|   |   |   |   |   |   |   \-- streamlit_callback_handler.py
|   |   |   |   |   |   |-- tracers
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- comet.py
|   |   |   |   |   |   |   |-- evaluation.py
|   |   |   |   |   |   |   |-- langchain.py
|   |   |   |   |   |   |   |-- log_stream.py
|   |   |   |   |   |   |   |-- logging.py
|   |   |   |   |   |   |   |-- root_listeners.py
|   |   |   |   |   |   |   |-- run_collector.py
|   |   |   |   |   |   |   |-- schemas.py
|   |   |   |   |   |   |   |-- stdout.py
|   |   |   |   |   |   |   \-- wandb.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- aim_callback.py
|   |   |   |   |   |   |-- argilla_callback.py
|   |   |   |   |   |   |-- arize_callback.py
|   |   |   |   |   |   |-- arthur_callback.py
|   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |-- clearml_callback.py
|   |   |   |   |   |   |-- comet_ml_callback.py
|   |   |   |   |   |   |-- confident_callback.py
|   |   |   |   |   |   |-- context_callback.py
|   |   |   |   |   |   |-- file.py
|   |   |   |   |   |   |-- flyte_callback.py
|   |   |   |   |   |   |-- human.py
|   |   |   |   |   |   |-- infino_callback.py
|   |   |   |   |   |   |-- labelstudio_callback.py
|   |   |   |   |   |   |-- llmonitor_callback.py
|   |   |   |   |   |   |-- manager.py
|   |   |   |   |   |   |-- mlflow_callback.py
|   |   |   |   |   |   |-- openai_info.py
|   |   |   |   |   |   |-- promptlayer_callback.py
|   |   |   |   |   |   |-- sagemaker_callback.py
|   |   |   |   |   |   |-- stdout.py
|   |   |   |   |   |   |-- streaming_aiter.py
|   |   |   |   |   |   |-- streaming_aiter_final_only.py
|   |   |   |   |   |   |-- streaming_stdout.py
|   |   |   |   |   |   |-- streaming_stdout_final_only.py
|   |   |   |   |   |   |-- trubrics_callback.py
|   |   |   |   |   |   |-- utils.py
|   |   |   |   |   |   |-- wandb_callback.py
|   |   |   |   |   |   \-- whylabs_callback.py
|   |   |   |   |   |-- chains
|   |   |   |   |   |   |-- api
|   |   |   |   |   |   |   |-- openapi
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- chain.py
|   |   |   |   |   |   |   |   |-- prompts.py
|   |   |   |   |   |   |   |   |-- requests_chain.py
|   |   |   |   |   |   |   |   \-- response_chain.py
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- news_docs.py
|   |   |   |   |   |   |   |-- open_meteo_docs.py
|   |   |   |   |   |   |   |-- podcast_docs.py
|   |   |   |   |   |   |   |-- prompt.py
|   |   |   |   |   |   |   \-- tmdb_docs.py
|   |   |   |   |   |   |-- chat_vector_db
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- prompts.py
|   |   |   |   |   |   |-- combine_documents
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- map_reduce.py
|   |   |   |   |   |   |   |-- map_rerank.py
|   |   |   |   |   |   |   |-- reduce.py
|   |   |   |   |   |   |   |-- refine.py
|   |   |   |   |   |   |   \-- stuff.py
|   |   |   |   |   |   |-- constitutional_ai
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- models.py
|   |   |   |   |   |   |   |-- principles.py
|   |   |   |   |   |   |   \-- prompts.py
|   |   |   |   |   |   |-- conversation
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- memory.py
|   |   |   |   |   |   |   \-- prompt.py
|   |   |   |   |   |   |-- conversational_retrieval
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   \-- prompts.py
|   |   |   |   |   |   |-- elasticsearch_database
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   \-- prompts.py
|   |   |   |   |   |   |-- ernie_functions
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- base.py
|   |   |   |   |   |   |-- flare
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   \-- prompts.py
|   |   |   |   |   |   |-- graph_qa
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- arangodb.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- cypher.py
|   |   |   |   |   |   |   |-- cypher_utils.py
|   |   |   |   |   |   |   |-- falkordb.py
|   |   |   |   |   |   |   |-- gremlin.py
|   |   |   |   |   |   |   |-- hugegraph.py
|   |   |   |   |   |   |   |-- kuzu.py
|   |   |   |   |   |   |   |-- nebulagraph.py
|   |   |   |   |   |   |   |-- neptune_cypher.py
|   |   |   |   |   |   |   |-- neptune_sparql.py
|   |   |   |   |   |   |   |-- ontotext_graphdb.py
|   |   |   |   |   |   |   |-- prompts.py
|   |   |   |   |   |   |   \-- sparql.py
|   |   |   |   |   |   |-- hyde
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   \-- prompts.py
|   |   |   |   |   |   |-- llm_bash
|   |   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |   |-- llm_checker
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   \-- prompt.py
|   |   |   |   |   |   |-- llm_math
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   \-- prompt.py
|   |   |   |   |   |   |-- llm_summarization_checker
|   |   |   |   |   |   |   |-- prompts
|   |   |   |   |   |   |   |   |-- are_all_true_prompt.txt
|   |   |   |   |   |   |   |   |-- check_facts.txt
|   |   |   |   |   |   |   |   |-- create_facts.txt
|   |   |   |   |   |   |   |   \-- revise_summary.txt
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- base.py
|   |   |   |   |   |   |-- llm_symbolic_math
|   |   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |   |-- natbot
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- crawler.py
|   |   |   |   |   |   |   \-- prompt.py
|   |   |   |   |   |   |-- openai_functions
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- citation_fuzzy_match.py
|   |   |   |   |   |   |   |-- extraction.py
|   |   |   |   |   |   |   |-- openapi.py
|   |   |   |   |   |   |   |-- qa_with_structure.py
|   |   |   |   |   |   |   |-- tagging.py
|   |   |   |   |   |   |   \-- utils.py
|   |   |   |   |   |   |-- openai_tools
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- extraction.py
|   |   |   |   |   |   |-- qa_generation
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   \-- prompt.py
|   |   |   |   |   |   |-- qa_with_sources
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- loading.py
|   |   |   |   |   |   |   |-- map_reduce_prompt.py
|   |   |   |   |   |   |   |-- refine_prompts.py
|   |   |   |   |   |   |   |-- retrieval.py
|   |   |   |   |   |   |   |-- stuff_prompt.py
|   |   |   |   |   |   |   \-- vector_db.py
|   |   |   |   |   |   |-- query_constructor
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- ir.py
|   |   |   |   |   |   |   |-- parser.py
|   |   |   |   |   |   |   |-- prompt.py
|   |   |   |   |   |   |   \-- schema.py
|   |   |   |   |   |   |-- question_answering
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- chain.py
|   |   |   |   |   |   |   |-- map_reduce_prompt.py
|   |   |   |   |   |   |   |-- map_rerank_prompt.py
|   |   |   |   |   |   |   |-- refine_prompts.py
|   |   |   |   |   |   |   \-- stuff_prompt.py
|   |   |   |   |   |   |-- retrieval_qa
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   \-- prompt.py
|   |   |   |   |   |   |-- router
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- embedding_router.py
|   |   |   |   |   |   |   |-- llm_router.py
|   |   |   |   |   |   |   |-- multi_prompt.py
|   |   |   |   |   |   |   |-- multi_prompt_prompt.py
|   |   |   |   |   |   |   |-- multi_retrieval_prompt.py
|   |   |   |   |   |   |   \-- multi_retrieval_qa.py
|   |   |   |   |   |   |-- sql_database
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- prompt.py
|   |   |   |   |   |   |   \-- query.py
|   |   |   |   |   |   |-- structured_output
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- base.py
|   |   |   |   |   |   |-- summarize
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- chain.py
|   |   |   |   |   |   |   |-- map_reduce_prompt.py
|   |   |   |   |   |   |   |-- refine_prompts.py
|   |   |   |   |   |   |   \-- stuff_prompt.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |-- example_generator.py
|   |   |   |   |   |   |-- history_aware_retriever.py
|   |   |   |   |   |   |-- llm.py
|   |   |   |   |   |   |-- llm_requests.py
|   |   |   |   |   |   |-- loading.py
|   |   |   |   |   |   |-- mapreduce.py
|   |   |   |   |   |   |-- moderation.py
|   |   |   |   |   |   |-- prompt_selector.py
|   |   |   |   |   |   |-- retrieval.py
|   |   |   |   |   |   |-- sequential.py
|   |   |   |   |   |   \-- transform.py
|   |   |   |   |   |-- chat_loaders
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |-- facebook_messenger.py
|   |   |   |   |   |   |-- gmail.py
|   |   |   |   |   |   |-- imessage.py
|   |   |   |   |   |   |-- langsmith.py
|   |   |   |   |   |   |-- slack.py
|   |   |   |   |   |   |-- telegram.py
|   |   |   |   |   |   |-- utils.py
|   |   |   |   |   |   \-- whatsapp.py
|   |   |   |   |   |-- chat_models
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- anthropic.py
|   |   |   |   |   |   |-- anyscale.py
|   |   |   |   |   |   |-- azure_openai.py
|   |   |   |   |   |   |-- azureml_endpoint.py
|   |   |   |   |   |   |-- baichuan.py
|   |   |   |   |   |   |-- baidu_qianfan_endpoint.py
|   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |-- bedrock.py
|   |   |   |   |   |   |-- cohere.py
|   |   |   |   |   |   |-- databricks.py
|   |   |   |   |   |   |-- ernie.py
|   |   |   |   |   |   |-- everlyai.py
|   |   |   |   |   |   |-- fake.py
|   |   |   |   |   |   |-- fireworks.py
|   |   |   |   |   |   |-- gigachat.py
|   |   |   |   |   |   |-- google_palm.py
|   |   |   |   |   |   |-- human.py
|   |   |   |   |   |   |-- hunyuan.py
|   |   |   |   |   |   |-- javelin_ai_gateway.py
|   |   |   |   |   |   |-- jinachat.py
|   |   |   |   |   |   |-- konko.py
|   |   |   |   |   |   |-- litellm.py
|   |   |   |   |   |   |-- meta.py
|   |   |   |   |   |   |-- minimax.py
|   |   |   |   |   |   |-- mlflow.py
|   |   |   |   |   |   |-- mlflow_ai_gateway.py
|   |   |   |   |   |   |-- ollama.py
|   |   |   |   |   |   |-- openai.py
|   |   |   |   |   |   |-- pai_eas_endpoint.py
|   |   |   |   |   |   |-- promptlayer_openai.py
|   |   |   |   |   |   |-- tongyi.py
|   |   |   |   |   |   |-- vertexai.py
|   |   |   |   |   |   |-- volcengine_maas.py
|   |   |   |   |   |   \-- yandex.py
|   |   |   |   |   |-- docstore
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- arbitrary_fn.py
|   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |-- document.py
|   |   |   |   |   |   |-- in_memory.py
|   |   |   |   |   |   \-- wikipedia.py
|   |   |   |   |   |-- document_loaders
|   |   |   |   |   |   |-- blob_loaders
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- file_system.py
|   |   |   |   |   |   |   |-- schema.py
|   |   |   |   |   |   |   \-- youtube_audio.py
|   |   |   |   |   |   |-- parsers
|   |   |   |   |   |   |   |-- html
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- bs4.py
|   |   |   |   |   |   |   |-- language
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- cobol.py
|   |   |   |   |   |   |   |   |-- code_segmenter.py
|   |   |   |   |   |   |   |   |-- javascript.py
|   |   |   |   |   |   |   |   |-- language_parser.py
|   |   |   |   |   |   |   |   \-- python.py
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- audio.py
|   |   |   |   |   |   |   |-- docai.py
|   |   |   |   |   |   |   |-- generic.py
|   |   |   |   |   |   |   |-- grobid.py
|   |   |   |   |   |   |   |-- msword.py
|   |   |   |   |   |   |   |-- pdf.py
|   |   |   |   |   |   |   |-- registry.py
|   |   |   |   |   |   |   \-- txt.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- acreom.py
|   |   |   |   |   |   |-- airbyte.py
|   |   |   |   |   |   |-- airbyte_json.py
|   |   |   |   |   |   |-- airtable.py
|   |   |   |   |   |   |-- apify_dataset.py
|   |   |   |   |   |   |-- arcgis_loader.py
|   |   |   |   |   |   |-- arxiv.py
|   |   |   |   |   |   |-- assemblyai.py
|   |   |   |   |   |   |-- async_html.py
|   |   |   |   |   |   |-- azlyrics.py
|   |   |   |   |   |   |-- azure_ai_data.py
|   |   |   |   |   |   |-- azure_blob_storage_container.py
|   |   |   |   |   |   |-- azure_blob_storage_file.py
|   |   |   |   |   |   |-- baiducloud_bos_directory.py
|   |   |   |   |   |   |-- baiducloud_bos_file.py
|   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |-- base_o365.py
|   |   |   |   |   |   |-- bibtex.py
|   |   |   |   |   |   |-- bigquery.py
|   |   |   |   |   |   |-- bilibili.py
|   |   |   |   |   |   |-- blackboard.py
|   |   |   |   |   |   |-- blockchain.py
|   |   |   |   |   |   |-- brave_search.py
|   |   |   |   |   |   |-- browserless.py
|   |   |   |   |   |   |-- chatgpt.py
|   |   |   |   |   |   |-- chromium.py
|   |   |   |   |   |   |-- college_confidential.py
|   |   |   |   |   |   |-- concurrent.py
|   |   |   |   |   |   |-- confluence.py
|   |   |   |   |   |   |-- conllu.py
|   |   |   |   |   |   |-- couchbase.py
|   |   |   |   |   |   |-- csv_loader.py
|   |   |   |   |   |   |-- cube_semantic.py
|   |   |   |   |   |   |-- datadog_logs.py
|   |   |   |   |   |   |-- dataframe.py
|   |   |   |   |   |   |-- diffbot.py
|   |   |   |   |   |   |-- directory.py
|   |   |   |   |   |   |-- discord.py
|   |   |   |   |   |   |-- docugami.py
|   |   |   |   |   |   |-- docusaurus.py
|   |   |   |   |   |   |-- dropbox.py
|   |   |   |   |   |   |-- duckdb_loader.py
|   |   |   |   |   |   |-- email.py
|   |   |   |   |   |   |-- epub.py
|   |   |   |   |   |   |-- etherscan.py
|   |   |   |   |   |   |-- evernote.py
|   |   |   |   |   |   |-- excel.py
|   |   |   |   |   |   |-- facebook_chat.py
|   |   |   |   |   |   |-- fauna.py
|   |   |   |   |   |   |-- figma.py
|   |   |   |   |   |   |-- gcs_directory.py
|   |   |   |   |   |   |-- gcs_file.py
|   |   |   |   |   |   |-- generic.py
|   |   |   |   |   |   |-- geodataframe.py
|   |   |   |   |   |   |-- git.py
|   |   |   |   |   |   |-- gitbook.py
|   |   |   |   |   |   |-- github.py
|   |   |   |   |   |   |-- google_speech_to_text.py
|   |   |   |   |   |   |-- googledrive.py
|   |   |   |   |   |   |-- gutenberg.py
|   |   |   |   |   |   |-- helpers.py
|   |   |   |   |   |   |-- hn.py
|   |   |   |   |   |   |-- html.py
|   |   |   |   |   |   |-- html_bs.py
|   |   |   |   |   |   |-- hugging_face_dataset.py
|   |   |   |   |   |   |-- ifixit.py
|   |   |   |   |   |   |-- image.py
|   |   |   |   |   |   |-- image_captions.py
|   |   |   |   |   |   |-- imsdb.py
|   |   |   |   |   |   |-- iugu.py
|   |   |   |   |   |   |-- joplin.py
|   |   |   |   |   |   |-- json_loader.py
|   |   |   |   |   |   |-- lakefs.py
|   |   |   |   |   |   |-- larksuite.py
|   |   |   |   |   |   |-- markdown.py
|   |   |   |   |   |   |-- mastodon.py
|   |   |   |   |   |   |-- max_compute.py
|   |   |   |   |   |   |-- mediawikidump.py
|   |   |   |   |   |   |-- merge.py
|   |   |   |   |   |   |-- mhtml.py
|   |   |   |   |   |   |-- modern_treasury.py
|   |   |   |   |   |   |-- mongodb.py
|   |   |   |   |   |   |-- news.py
|   |   |   |   |   |   |-- notebook.py
|   |   |   |   |   |   |-- notion.py
|   |   |   |   |   |   |-- notiondb.py
|   |   |   |   |   |   |-- nuclia.py
|   |   |   |   |   |   |-- obs_directory.py
|   |   |   |   |   |   |-- obs_file.py
|   |   |   |   |   |   |-- obsidian.py
|   |   |   |   |   |   |-- odt.py
|   |   |   |   |   |   |-- onedrive.py
|   |   |   |   |   |   |-- onedrive_file.py
|   |   |   |   |   |   |-- onenote.py
|   |   |   |   |   |   |-- open_city_data.py
|   |   |   |   |   |   |-- org_mode.py
|   |   |   |   |   |   |-- pdf.py
|   |   |   |   |   |   |-- polars_dataframe.py
|   |   |   |   |   |   |-- powerpoint.py
|   |   |   |   |   |   |-- psychic.py
|   |   |   |   |   |   |-- pubmed.py
|   |   |   |   |   |   |-- pyspark_dataframe.py
|   |   |   |   |   |   |-- python.py
|   |   |   |   |   |   |-- quip.py
|   |   |   |   |   |   |-- readthedocs.py
|   |   |   |   |   |   |-- recursive_url_loader.py
|   |   |   |   |   |   |-- reddit.py
|   |   |   |   |   |   |-- roam.py
|   |   |   |   |   |   |-- rocksetdb.py
|   |   |   |   |   |   |-- rspace.py
|   |   |   |   |   |   |-- rss.py
|   |   |   |   |   |   |-- rst.py
|   |   |   |   |   |   |-- rtf.py
|   |   |   |   |   |   |-- s3_directory.py
|   |   |   |   |   |   |-- s3_file.py
|   |   |   |   |   |   |-- sharepoint.py
|   |   |   |   |   |   |-- sitemap.py
|   |   |   |   |   |   |-- slack_directory.py
|   |   |   |   |   |   |-- snowflake_loader.py
|   |   |   |   |   |   |-- spreedly.py
|   |   |   |   |   |   |-- srt.py
|   |   |   |   |   |   |-- stripe.py
|   |   |   |   |   |   |-- telegram.py
|   |   |   |   |   |   |-- tencent_cos_directory.py
|   |   |   |   |   |   |-- tencent_cos_file.py
|   |   |   |   |   |   |-- tensorflow_datasets.py
|   |   |   |   |   |   |-- text.py
|   |   |   |   |   |   |-- tomarkdown.py
|   |   |   |   |   |   |-- toml.py
|   |   |   |   |   |   |-- trello.py
|   |   |   |   |   |   |-- tsv.py
|   |   |   |   |   |   |-- twitter.py
|   |   |   |   |   |   |-- unstructured.py
|   |   |   |   |   |   |-- url.py
|   |   |   |   |   |   |-- url_playwright.py
|   |   |   |   |   |   |-- url_selenium.py
|   |   |   |   |   |   |-- weather.py
|   |   |   |   |   |   |-- web_base.py
|   |   |   |   |   |   |-- whatsapp_chat.py
|   |   |   |   |   |   |-- wikipedia.py
|   |   |   |   |   |   |-- word_document.py
|   |   |   |   |   |   |-- xml.py
|   |   |   |   |   |   |-- xorbits.py
|   |   |   |   |   |   \-- youtube.py
|   |   |   |   |   |-- document_transformers
|   |   |   |   |   |   |-- xsl
|   |   |   |   |   |   |   \-- html_chunks_with_headers.xslt
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- beautiful_soup_transformer.py
|   |   |   |   |   |   |-- doctran_text_extract.py
|   |   |   |   |   |   |-- doctran_text_qa.py
|   |   |   |   |   |   |-- doctran_text_translate.py
|   |   |   |   |   |   |-- embeddings_redundant_filter.py
|   |   |   |   |   |   |-- google_translate.py
|   |   |   |   |   |   |-- html2text.py
|   |   |   |   |   |   |-- long_context_reorder.py
|   |   |   |   |   |   |-- nuclia_text_transform.py
|   |   |   |   |   |   \-- openai_functions.py
|   |   |   |   |   |-- embeddings
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- aleph_alpha.py
|   |   |   |   |   |   |-- awa.py
|   |   |   |   |   |   |-- azure_openai.py
|   |   |   |   |   |   |-- baidu_qianfan_endpoint.py
|   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |-- bedrock.py
|   |   |   |   |   |   |-- bookend.py
|   |   |   |   |   |   |-- cache.py
|   |   |   |   |   |   |-- clarifai.py
|   |   |   |   |   |   |-- cloudflare_workersai.py
|   |   |   |   |   |   |-- cohere.py
|   |   |   |   |   |   |-- dashscope.py
|   |   |   |   |   |   |-- databricks.py
|   |   |   |   |   |   |-- deepinfra.py
|   |   |   |   |   |   |-- edenai.py
|   |   |   |   |   |   |-- elasticsearch.py
|   |   |   |   |   |   |-- embaas.py
|   |   |   |   |   |   |-- ernie.py
|   |   |   |   |   |   |-- fake.py
|   |   |   |   |   |   |-- fastembed.py
|   |   |   |   |   |   |-- google_palm.py
|   |   |   |   |   |   |-- gpt4all.py
|   |   |   |   |   |   |-- gradient_ai.py
|   |   |   |   |   |   |-- huggingface.py
|   |   |   |   |   |   |-- huggingface_hub.py
|   |   |   |   |   |   |-- infinity.py
|   |   |   |   |   |   |-- javelin_ai_gateway.py
|   |   |   |   |   |   |-- jina.py
|   |   |   |   |   |   |-- johnsnowlabs.py
|   |   |   |   |   |   |-- llamacpp.py
|   |   |   |   |   |   |-- llm_rails.py
|   |   |   |   |   |   |-- localai.py
|   |   |   |   |   |   |-- minimax.py
|   |   |   |   |   |   |-- mlflow.py
|   |   |   |   |   |   |-- mlflow_gateway.py
|   |   |   |   |   |   |-- modelscope_hub.py
|   |   |   |   |   |   |-- mosaicml.py
|   |   |   |   |   |   |-- nlpcloud.py
|   |   |   |   |   |   |-- octoai_embeddings.py
|   |   |   |   |   |   |-- ollama.py
|   |   |   |   |   |   |-- openai.py
|   |   |   |   |   |   |-- sagemaker_endpoint.py
|   |   |   |   |   |   |-- self_hosted.py
|   |   |   |   |   |   |-- self_hosted_hugging_face.py
|   |   |   |   |   |   |-- sentence_transformer.py
|   |   |   |   |   |   |-- spacy_embeddings.py
|   |   |   |   |   |   |-- tensorflow_hub.py
|   |   |   |   |   |   |-- vertexai.py
|   |   |   |   |   |   |-- voyageai.py
|   |   |   |   |   |   \-- xinference.py
|   |   |   |   |   |-- evaluation
|   |   |   |   |   |   |-- agents
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- trajectory_eval_chain.py
|   |   |   |   |   |   |   \-- trajectory_eval_prompt.py
|   |   |   |   |   |   |-- comparison
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- eval_chain.py
|   |   |   |   |   |   |   \-- prompt.py
|   |   |   |   |   |   |-- criteria
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- eval_chain.py
|   |   |   |   |   |   |   \-- prompt.py
|   |   |   |   |   |   |-- embedding_distance
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- base.py
|   |   |   |   |   |   |-- exact_match
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- base.py
|   |   |   |   |   |   |-- parsing
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- json_distance.py
|   |   |   |   |   |   |   \-- json_schema.py
|   |   |   |   |   |   |-- qa
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- eval_chain.py
|   |   |   |   |   |   |   |-- eval_prompt.py
|   |   |   |   |   |   |   |-- generate_chain.py
|   |   |   |   |   |   |   \-- generate_prompt.py
|   |   |   |   |   |   |-- regex_match
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- base.py
|   |   |   |   |   |   |-- scoring
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- eval_chain.py
|   |   |   |   |   |   |   \-- prompt.py
|   |   |   |   |   |   |-- string_distance
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- base.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- loading.py
|   |   |   |   |   |   \-- schema.py
|   |   |   |   |   |-- graphs
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- arangodb_graph.py
|   |   |   |   |   |   |-- falkordb_graph.py
|   |   |   |   |   |   |-- graph_document.py
|   |   |   |   |   |   |-- graph_store.py
|   |   |   |   |   |   |-- hugegraph.py
|   |   |   |   |   |   |-- kuzu_graph.py
|   |   |   |   |   |   |-- memgraph_graph.py
|   |   |   |   |   |   |-- nebula_graph.py
|   |   |   |   |   |   |-- neo4j_graph.py
|   |   |   |   |   |   |-- neptune_graph.py
|   |   |   |   |   |   |-- networkx_graph.py
|   |   |   |   |   |   \-- rdf_graph.py
|   |   |   |   |   |-- indexes
|   |   |   |   |   |   |-- prompts
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- entity_extraction.py
|   |   |   |   |   |   |   |-- entity_summarization.py
|   |   |   |   |   |   |   \-- knowledge_triplet_extraction.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- _api.py
|   |   |   |   |   |   |-- _sql_record_manager.py
|   |   |   |   |   |   |-- graph.py
|   |   |   |   |   |   \-- vectorstore.py
|   |   |   |   |   |-- llms
|   |   |   |   |   |   |-- grammars
|   |   |   |   |   |   |   |-- json.gbnf
|   |   |   |   |   |   |   \-- list.gbnf
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- ai21.py
|   |   |   |   |   |   |-- aleph_alpha.py
|   |   |   |   |   |   |-- amazon_api_gateway.py
|   |   |   |   |   |   |-- anthropic.py
|   |   |   |   |   |   |-- anyscale.py
|   |   |   |   |   |   |-- arcee.py
|   |   |   |   |   |   |-- aviary.py
|   |   |   |   |   |   |-- azureml_endpoint.py
|   |   |   |   |   |   |-- baidu_qianfan_endpoint.py
|   |   |   |   |   |   |-- bananadev.py
|   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |-- baseten.py
|   |   |   |   |   |   |-- beam.py
|   |   |   |   |   |   |-- bedrock.py
|   |   |   |   |   |   |-- bittensor.py
|   |   |   |   |   |   |-- cerebriumai.py
|   |   |   |   |   |   |-- chatglm.py
|   |   |   |   |   |   |-- clarifai.py
|   |   |   |   |   |   |-- cloudflare_workersai.py
|   |   |   |   |   |   |-- cohere.py
|   |   |   |   |   |   |-- ctransformers.py
|   |   |   |   |   |   |-- ctranslate2.py
|   |   |   |   |   |   |-- databricks.py
|   |   |   |   |   |   |-- deepinfra.py
|   |   |   |   |   |   |-- deepsparse.py
|   |   |   |   |   |   |-- edenai.py
|   |   |   |   |   |   |-- fake.py
|   |   |   |   |   |   |-- fireworks.py
|   |   |   |   |   |   |-- forefrontai.py
|   |   |   |   |   |   |-- gigachat.py
|   |   |   |   |   |   |-- google_palm.py
|   |   |   |   |   |   |-- gooseai.py
|   |   |   |   |   |   |-- gpt4all.py
|   |   |   |   |   |   |-- gradient_ai.py
|   |   |   |   |   |   |-- huggingface_endpoint.py
|   |   |   |   |   |   |-- huggingface_hub.py
|   |   |   |   |   |   |-- huggingface_pipeline.py
|   |   |   |   |   |   |-- huggingface_text_gen_inference.py
|   |   |   |   |   |   |-- human.py
|   |   |   |   |   |   |-- javelin_ai_gateway.py
|   |   |   |   |   |   |-- koboldai.py
|   |   |   |   |   |   |-- llamacpp.py
|   |   |   |   |   |   |-- loading.py
|   |   |   |   |   |   |-- manifest.py
|   |   |   |   |   |   |-- minimax.py
|   |   |   |   |   |   |-- mlflow.py
|   |   |   |   |   |   |-- mlflow_ai_gateway.py
|   |   |   |   |   |   |-- modal.py
|   |   |   |   |   |   |-- mosaicml.py
|   |   |   |   |   |   |-- nlpcloud.py
|   |   |   |   |   |   |-- octoai_endpoint.py
|   |   |   |   |   |   |-- ollama.py
|   |   |   |   |   |   |-- opaqueprompts.py
|   |   |   |   |   |   |-- openai.py
|   |   |   |   |   |   |-- openllm.py
|   |   |   |   |   |   |-- openlm.py
|   |   |   |   |   |   |-- pai_eas_endpoint.py
|   |   |   |   |   |   |-- petals.py
|   |   |   |   |   |   |-- pipelineai.py
|   |   |   |   |   |   |-- predibase.py
|   |   |   |   |   |   |-- predictionguard.py
|   |   |   |   |   |   |-- promptlayer_openai.py
|   |   |   |   |   |   |-- replicate.py
|   |   |   |   |   |   |-- rwkv.py
|   |   |   |   |   |   |-- sagemaker_endpoint.py
|   |   |   |   |   |   |-- self_hosted.py
|   |   |   |   |   |   |-- self_hosted_hugging_face.py
|   |   |   |   |   |   |-- stochasticai.py
|   |   |   |   |   |   |-- symblai_nebula.py
|   |   |   |   |   |   |-- textgen.py
|   |   |   |   |   |   |-- titan_takeoff.py
|   |   |   |   |   |   |-- titan_takeoff_pro.py
|   |   |   |   |   |   |-- together.py
|   |   |   |   |   |   |-- tongyi.py
|   |   |   |   |   |   |-- utils.py
|   |   |   |   |   |   |-- vertexai.py
|   |   |   |   |   |   |-- vllm.py
|   |   |   |   |   |   |-- volcengine_maas.py
|   |   |   |   |   |   |-- watsonxllm.py
|   |   |   |   |   |   |-- writer.py
|   |   |   |   |   |   |-- xinference.py
|   |   |   |   |   |   \-- yandex.py
|   |   |   |   |   |-- load
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- dump.py
|   |   |   |   |   |   |-- load.py
|   |   |   |   |   |   \-- serializable.py
|   |   |   |   |   |-- memory
|   |   |   |   |   |   |-- chat_message_histories
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- astradb.py
|   |   |   |   |   |   |   |-- cassandra.py
|   |   |   |   |   |   |   |-- cosmos_db.py
|   |   |   |   |   |   |   |-- dynamodb.py
|   |   |   |   |   |   |   |-- elasticsearch.py
|   |   |   |   |   |   |   |-- file.py
|   |   |   |   |   |   |   |-- firestore.py
|   |   |   |   |   |   |   |-- in_memory.py
|   |   |   |   |   |   |   |-- momento.py
|   |   |   |   |   |   |   |-- mongodb.py
|   |   |   |   |   |   |   |-- neo4j.py
|   |   |   |   |   |   |   |-- postgres.py
|   |   |   |   |   |   |   |-- redis.py
|   |   |   |   |   |   |   |-- rocksetdb.py
|   |   |   |   |   |   |   |-- singlestoredb.py
|   |   |   |   |   |   |   |-- sql.py
|   |   |   |   |   |   |   |-- streamlit.py
|   |   |   |   |   |   |   |-- upstash_redis.py
|   |   |   |   |   |   |   |-- xata.py
|   |   |   |   |   |   |   \-- zep.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- buffer.py
|   |   |   |   |   |   |-- buffer_window.py
|   |   |   |   |   |   |-- chat_memory.py
|   |   |   |   |   |   |-- combined.py
|   |   |   |   |   |   |-- entity.py
|   |   |   |   |   |   |-- kg.py
|   |   |   |   |   |   |-- motorhead_memory.py
|   |   |   |   |   |   |-- prompt.py
|   |   |   |   |   |   |-- readonly.py
|   |   |   |   |   |   |-- simple.py
|   |   |   |   |   |   |-- summary.py
|   |   |   |   |   |   |-- summary_buffer.py
|   |   |   |   |   |   |-- token_buffer.py
|   |   |   |   |   |   |-- utils.py
|   |   |   |   |   |   |-- vectorstore.py
|   |   |   |   |   |   |-- vectorstore_token_buffer_memory.py
|   |   |   |   |   |   \-- zep_memory.py
|   |   |   |   |   |-- output_parsers
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- boolean.py
|   |   |   |   |   |   |-- combining.py
|   |   |   |   |   |   |-- datetime.py
|   |   |   |   |   |   |-- enum.py
|   |   |   |   |   |   |-- ernie_functions.py
|   |   |   |   |   |   |-- fix.py
|   |   |   |   |   |   |-- format_instructions.py
|   |   |   |   |   |   |-- json.py
|   |   |   |   |   |   |-- list.py
|   |   |   |   |   |   |-- loading.py
|   |   |   |   |   |   |-- openai_functions.py
|   |   |   |   |   |   |-- openai_tools.py
|   |   |   |   |   |   |-- pandas_dataframe.py
|   |   |   |   |   |   |-- prompts.py
|   |   |   |   |   |   |-- pydantic.py
|   |   |   |   |   |   |-- rail_parser.py
|   |   |   |   |   |   |-- regex.py
|   |   |   |   |   |   |-- regex_dict.py
|   |   |   |   |   |   |-- retry.py
|   |   |   |   |   |   |-- structured.py
|   |   |   |   |   |   |-- xml.py
|   |   |   |   |   |   \-- yaml.py
|   |   |   |   |   |-- prompts
|   |   |   |   |   |   |-- example_selector
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- length_based.py
|   |   |   |   |   |   |   |-- ngram_overlap.py
|   |   |   |   |   |   |   \-- semantic_similarity.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |-- chat.py
|   |   |   |   |   |   |-- few_shot.py
|   |   |   |   |   |   |-- few_shot_with_templates.py
|   |   |   |   |   |   |-- loading.py
|   |   |   |   |   |   \-- prompt.py
|   |   |   |   |   |-- retrievers
|   |   |   |   |   |   |-- document_compressors
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- chain_extract.py
|   |   |   |   |   |   |   |-- chain_extract_prompt.py
|   |   |   |   |   |   |   |-- chain_filter.py
|   |   |   |   |   |   |   |-- chain_filter_prompt.py
|   |   |   |   |   |   |   |-- cohere_rerank.py
|   |   |   |   |   |   |   |-- cross_encoder.py
|   |   |   |   |   |   |   |-- cross_encoder_rerank.py
|   |   |   |   |   |   |   |-- embeddings_filter.py
|   |   |   |   |   |   |   |-- flashrank_rerank.py
|   |   |   |   |   |   |   \-- listwise_rerank.py
|   |   |   |   |   |   |-- self_query
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- astradb.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- chroma.py
|   |   |   |   |   |   |   |-- dashvector.py
|   |   |   |   |   |   |   |-- databricks_vector_search.py
|   |   |   |   |   |   |   |-- deeplake.py
|   |   |   |   |   |   |   |-- dingo.py
|   |   |   |   |   |   |   |-- elasticsearch.py
|   |   |   |   |   |   |   |-- milvus.py
|   |   |   |   |   |   |   |-- mongodb_atlas.py
|   |   |   |   |   |   |   |-- myscale.py
|   |   |   |   |   |   |   |-- opensearch.py
|   |   |   |   |   |   |   |-- pgvector.py
|   |   |   |   |   |   |   |-- pinecone.py
|   |   |   |   |   |   |   |-- qdrant.py
|   |   |   |   |   |   |   |-- redis.py
|   |   |   |   |   |   |   |-- supabase.py
|   |   |   |   |   |   |   |-- tencentvectordb.py
|   |   |   |   |   |   |   |-- timescalevector.py
|   |   |   |   |   |   |   |-- vectara.py
|   |   |   |   |   |   |   \-- weaviate.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- arcee.py
|   |   |   |   |   |   |-- arxiv.py
|   |   |   |   |   |   |-- azure_ai_search.py
|   |   |   |   |   |   |-- bedrock.py
|   |   |   |   |   |   |-- bm25.py
|   |   |   |   |   |   |-- chaindesk.py
|   |   |   |   |   |   |-- chatgpt_plugin_retriever.py
|   |   |   |   |   |   |-- cohere_rag_retriever.py
|   |   |   |   |   |   |-- contextual_compression.py
|   |   |   |   |   |   |-- databerry.py
|   |   |   |   |   |   |-- docarray.py
|   |   |   |   |   |   |-- elastic_search_bm25.py
|   |   |   |   |   |   |-- embedchain.py
|   |   |   |   |   |   |-- ensemble.py
|   |   |   |   |   |   |-- google_cloud_documentai_warehouse.py
|   |   |   |   |   |   |-- google_vertex_ai_search.py
|   |   |   |   |   |   |-- kay.py
|   |   |   |   |   |   |-- kendra.py
|   |   |   |   |   |   |-- knn.py
|   |   |   |   |   |   |-- llama_index.py
|   |   |   |   |   |   |-- merger_retriever.py
|   |   |   |   |   |   |-- metal.py
|   |   |   |   |   |   |-- milvus.py
|   |   |   |   |   |   |-- multi_query.py
|   |   |   |   |   |   |-- multi_vector.py
|   |   |   |   |   |   |-- outline.py
|   |   |   |   |   |   |-- parent_document_retriever.py
|   |   |   |   |   |   |-- pinecone_hybrid_search.py
|   |   |   |   |   |   |-- pubmed.py
|   |   |   |   |   |   |-- pupmed.py
|   |   |   |   |   |   |-- re_phraser.py
|   |   |   |   |   |   |-- remote_retriever.py
|   |   |   |   |   |   |-- svm.py
|   |   |   |   |   |   |-- tavily_search_api.py
|   |   |   |   |   |   |-- tfidf.py
|   |   |   |   |   |   |-- time_weighted_retriever.py
|   |   |   |   |   |   |-- vespa_retriever.py
|   |   |   |   |   |   |-- weaviate_hybrid_search.py
|   |   |   |   |   |   |-- web_research.py
|   |   |   |   |   |   |-- wikipedia.py
|   |   |   |   |   |   |-- you.py
|   |   |   |   |   |   |-- zep.py
|   |   |   |   |   |   \-- zilliz.py
|   |   |   |   |   |-- runnables
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- hub.py
|   |   |   |   |   |   \-- openai_functions.py
|   |   |   |   |   |-- schema
|   |   |   |   |   |   |-- callbacks
|   |   |   |   |   |   |   |-- tracers
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |   |-- evaluation.py
|   |   |   |   |   |   |   |   |-- langchain.py
|   |   |   |   |   |   |   |   |-- log_stream.py
|   |   |   |   |   |   |   |   |-- root_listeners.py
|   |   |   |   |   |   |   |   |-- run_collector.py
|   |   |   |   |   |   |   |   |-- schemas.py
|   |   |   |   |   |   |   |   \-- stdout.py
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- manager.py
|   |   |   |   |   |   |   |-- stdout.py
|   |   |   |   |   |   |   \-- streaming_stdout.py
|   |   |   |   |   |   |-- runnable
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- branch.py
|   |   |   |   |   |   |   |-- config.py
|   |   |   |   |   |   |   |-- configurable.py
|   |   |   |   |   |   |   |-- fallbacks.py
|   |   |   |   |   |   |   |-- history.py
|   |   |   |   |   |   |   |-- passthrough.py
|   |   |   |   |   |   |   |-- retry.py
|   |   |   |   |   |   |   |-- router.py
|   |   |   |   |   |   |   \-- utils.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- agent.py
|   |   |   |   |   |   |-- cache.py
|   |   |   |   |   |   |-- chat.py
|   |   |   |   |   |   |-- chat_history.py
|   |   |   |   |   |   |-- document.py
|   |   |   |   |   |   |-- embeddings.py
|   |   |   |   |   |   |-- exceptions.py
|   |   |   |   |   |   |-- language_model.py
|   |   |   |   |   |   |-- memory.py
|   |   |   |   |   |   |-- messages.py
|   |   |   |   |   |   |-- output.py
|   |   |   |   |   |   |-- output_parser.py
|   |   |   |   |   |   |-- prompt.py
|   |   |   |   |   |   |-- prompt_template.py
|   |   |   |   |   |   |-- retriever.py
|   |   |   |   |   |   |-- storage.py
|   |   |   |   |   |   \-- vectorstore.py
|   |   |   |   |   |-- smith
|   |   |   |   |   |   |-- evaluation
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- config.py
|   |   |   |   |   |   |   |-- name_generation.py
|   |   |   |   |   |   |   |-- progress.py
|   |   |   |   |   |   |   |-- runner_utils.py
|   |   |   |   |   |   |   \-- string_run_evaluator.py
|   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |-- storage
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- _lc_store.py
|   |   |   |   |   |   |-- encoder_backed.py
|   |   |   |   |   |   |-- exceptions.py
|   |   |   |   |   |   |-- file_system.py
|   |   |   |   |   |   |-- in_memory.py
|   |   |   |   |   |   |-- redis.py
|   |   |   |   |   |   \-- upstash_redis.py
|   |   |   |   |   |-- tools
|   |   |   |   |   |   |-- ainetwork
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- app.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- owner.py
|   |   |   |   |   |   |   |-- rule.py
|   |   |   |   |   |   |   |-- transfer.py
|   |   |   |   |   |   |   \-- value.py
|   |   |   |   |   |   |-- amadeus
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- closest_airport.py
|   |   |   |   |   |   |   \-- flight_search.py
|   |   |   |   |   |   |-- arxiv
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- azure_cognitive_services
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- form_recognizer.py
|   |   |   |   |   |   |   |-- image_analysis.py
|   |   |   |   |   |   |   |-- speech2text.py
|   |   |   |   |   |   |   |-- text2speech.py
|   |   |   |   |   |   |   \-- text_analytics_health.py
|   |   |   |   |   |   |-- bearly
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- bing_search
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- brave_search
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- clickup
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- dataforseo_api_search
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- ddg_search
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- e2b_data_analysis
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- edenai
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- audio_speech_to_text.py
|   |   |   |   |   |   |   |-- audio_text_to_speech.py
|   |   |   |   |   |   |   |-- edenai_base_tool.py
|   |   |   |   |   |   |   |-- image_explicitcontent.py
|   |   |   |   |   |   |   |-- image_objectdetection.py
|   |   |   |   |   |   |   |-- ocr_identityparser.py
|   |   |   |   |   |   |   |-- ocr_invoiceparser.py
|   |   |   |   |   |   |   \-- text_moderation.py
|   |   |   |   |   |   |-- eleven_labs
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- models.py
|   |   |   |   |   |   |   \-- text2speech.py
|   |   |   |   |   |   |-- file_management
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- copy.py
|   |   |   |   |   |   |   |-- delete.py
|   |   |   |   |   |   |   |-- file_search.py
|   |   |   |   |   |   |   |-- list_dir.py
|   |   |   |   |   |   |   |-- move.py
|   |   |   |   |   |   |   |-- read.py
|   |   |   |   |   |   |   \-- write.py
|   |   |   |   |   |   |-- github
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- gitlab
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- gmail
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- create_draft.py
|   |   |   |   |   |   |   |-- get_message.py
|   |   |   |   |   |   |   |-- get_thread.py
|   |   |   |   |   |   |   |-- search.py
|   |   |   |   |   |   |   \-- send_message.py
|   |   |   |   |   |   |-- golden_query
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- google_cloud
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- texttospeech.py
|   |   |   |   |   |   |-- google_finance
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- google_jobs
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- google_lens
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- google_places
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- google_scholar
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- google_search
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- google_serper
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- google_trends
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- graphql
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- human
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- interaction
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- jira
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- json
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- memorize
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- merriam_webster
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- metaphor_search
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- multion
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- close_session.py
|   |   |   |   |   |   |   |-- create_session.py
|   |   |   |   |   |   |   \-- update_session.py
|   |   |   |   |   |   |-- nasa
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- nuclia
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- office365
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- create_draft_message.py
|   |   |   |   |   |   |   |-- events_search.py
|   |   |   |   |   |   |   |-- messages_search.py
|   |   |   |   |   |   |   |-- send_event.py
|   |   |   |   |   |   |   \-- send_message.py
|   |   |   |   |   |   |-- openapi
|   |   |   |   |   |   |   |-- utils
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- api_models.py
|   |   |   |   |   |   |   |   \-- openapi_utils.py
|   |   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |   |-- openweathermap
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- playwright
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- click.py
|   |   |   |   |   |   |   |-- current_page.py
|   |   |   |   |   |   |   |-- extract_hyperlinks.py
|   |   |   |   |   |   |   |-- extract_text.py
|   |   |   |   |   |   |   |-- get_elements.py
|   |   |   |   |   |   |   |-- navigate.py
|   |   |   |   |   |   |   \-- navigate_back.py
|   |   |   |   |   |   |-- powerbi
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- pubmed
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- python
|   |   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |   |-- reddit_search
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- requests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- scenexplain
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- searchapi
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- searx_search
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- shell
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- slack
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- get_channel.py
|   |   |   |   |   |   |   |-- get_message.py
|   |   |   |   |   |   |   |-- schedule_message.py
|   |   |   |   |   |   |   \-- send_message.py
|   |   |   |   |   |   |-- sleep
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- spark_sql
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- sql_database
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- prompt.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- stackexchange
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- steam
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- steamship_image_generation
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- tavily_search
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- vectorstore
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- wikipedia
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- wolfram_alpha
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- youtube
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- search.py
|   |   |   |   |   |   |-- zapier
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tool.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |-- convert_to_openai.py
|   |   |   |   |   |   |-- ifttt.py
|   |   |   |   |   |   |-- plugin.py
|   |   |   |   |   |   |-- render.py
|   |   |   |   |   |   |-- retriever.py
|   |   |   |   |   |   \-- yahoo_finance_news.py
|   |   |   |   |   |-- utilities
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- alpha_vantage.py
|   |   |   |   |   |   |-- anthropic.py
|   |   |   |   |   |   |-- apify.py
|   |   |   |   |   |   |-- arcee.py
|   |   |   |   |   |   |-- arxiv.py
|   |   |   |   |   |   |-- asyncio.py
|   |   |   |   |   |   |-- awslambda.py
|   |   |   |   |   |   |-- bibtex.py
|   |   |   |   |   |   |-- bing_search.py
|   |   |   |   |   |   |-- brave_search.py
|   |   |   |   |   |   |-- clickup.py
|   |   |   |   |   |   |-- dalle_image_generator.py
|   |   |   |   |   |   |-- dataforseo_api_search.py
|   |   |   |   |   |   |-- duckduckgo_search.py
|   |   |   |   |   |   |-- github.py
|   |   |   |   |   |   |-- gitlab.py
|   |   |   |   |   |   |-- golden_query.py
|   |   |   |   |   |   |-- google_finance.py
|   |   |   |   |   |   |-- google_jobs.py
|   |   |   |   |   |   |-- google_lens.py
|   |   |   |   |   |   |-- google_places_api.py
|   |   |   |   |   |   |-- google_scholar.py
|   |   |   |   |   |   |-- google_search.py
|   |   |   |   |   |   |-- google_serper.py
|   |   |   |   |   |   |-- google_trends.py
|   |   |   |   |   |   |-- graphql.py
|   |   |   |   |   |   |-- jira.py
|   |   |   |   |   |   |-- max_compute.py
|   |   |   |   |   |   |-- merriam_webster.py
|   |   |   |   |   |   |-- metaphor_search.py
|   |   |   |   |   |   |-- nasa.py
|   |   |   |   |   |   |-- opaqueprompts.py
|   |   |   |   |   |   |-- openapi.py
|   |   |   |   |   |   |-- openweathermap.py
|   |   |   |   |   |   |-- outline.py
|   |   |   |   |   |   |-- portkey.py
|   |   |   |   |   |   |-- powerbi.py
|   |   |   |   |   |   |-- pubmed.py
|   |   |   |   |   |   |-- python.py
|   |   |   |   |   |   |-- reddit_search.py
|   |   |   |   |   |   |-- redis.py
|   |   |   |   |   |   |-- requests.py
|   |   |   |   |   |   |-- scenexplain.py
|   |   |   |   |   |   |-- searchapi.py
|   |   |   |   |   |   |-- searx_search.py
|   |   |   |   |   |   |-- serpapi.py
|   |   |   |   |   |   |-- spark_sql.py
|   |   |   |   |   |   |-- sql_database.py
|   |   |   |   |   |   |-- stackexchange.py
|   |   |   |   |   |   |-- steam.py
|   |   |   |   |   |   |-- tavily_search.py
|   |   |   |   |   |   |-- tensorflow_datasets.py
|   |   |   |   |   |   |-- twilio.py
|   |   |   |   |   |   |-- vertexai.py
|   |   |   |   |   |   |-- wikipedia.py
|   |   |   |   |   |   |-- wolfram_alpha.py
|   |   |   |   |   |   \-- zapier.py
|   |   |   |   |   |-- utils
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- aiter.py
|   |   |   |   |   |   |-- env.py
|   |   |   |   |   |   |-- ernie_functions.py
|   |   |   |   |   |   |-- formatting.py
|   |   |   |   |   |   |-- html.py
|   |   |   |   |   |   |-- input.py
|   |   |   |   |   |   |-- iter.py
|   |   |   |   |   |   |-- json_schema.py
|   |   |   |   |   |   |-- math.py
|   |   |   |   |   |   |-- openai.py
|   |   |   |   |   |   |-- openai_functions.py
|   |   |   |   |   |   |-- pydantic.py
|   |   |   |   |   |   |-- strings.py
|   |   |   |   |   |   \-- utils.py
|   |   |   |   |   |-- vectorstores
|   |   |   |   |   |   |-- docarray
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- hnsw.py
|   |   |   |   |   |   |   \-- in_memory.py
|   |   |   |   |   |   |-- redis
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |-- filters.py
|   |   |   |   |   |   |   \-- schema.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- alibabacloud_opensearch.py
|   |   |   |   |   |   |-- analyticdb.py
|   |   |   |   |   |   |-- annoy.py
|   |   |   |   |   |   |-- astradb.py
|   |   |   |   |   |   |-- atlas.py
|   |   |   |   |   |   |-- awadb.py
|   |   |   |   |   |   |-- azure_cosmos_db.py
|   |   |   |   |   |   |-- azuresearch.py
|   |   |   |   |   |   |-- bageldb.py
|   |   |   |   |   |   |-- baiducloud_vector_search.py
|   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |-- cassandra.py
|   |   |   |   |   |   |-- chroma.py
|   |   |   |   |   |   |-- clarifai.py
|   |   |   |   |   |   |-- clickhouse.py
|   |   |   |   |   |   |-- dashvector.py
|   |   |   |   |   |   |-- databricks_vector_search.py
|   |   |   |   |   |   |-- deeplake.py
|   |   |   |   |   |   |-- dingo.py
|   |   |   |   |   |   |-- elastic_vector_search.py
|   |   |   |   |   |   |-- elasticsearch.py
|   |   |   |   |   |   |-- epsilla.py
|   |   |   |   |   |   |-- faiss.py
|   |   |   |   |   |   |-- hippo.py
|   |   |   |   |   |   |-- hologres.py
|   |   |   |   |   |   |-- lancedb.py
|   |   |   |   |   |   |-- llm_rails.py
|   |   |   |   |   |   |-- marqo.py
|   |   |   |   |   |   |-- matching_engine.py
|   |   |   |   |   |   |-- meilisearch.py
|   |   |   |   |   |   |-- milvus.py
|   |   |   |   |   |   |-- momento_vector_index.py
|   |   |   |   |   |   |-- mongodb_atlas.py
|   |   |   |   |   |   |-- myscale.py
|   |   |   |   |   |   |-- neo4j_vector.py
|   |   |   |   |   |   |-- nucliadb.py
|   |   |   |   |   |   |-- opensearch_vector_search.py
|   |   |   |   |   |   |-- pgembedding.py
|   |   |   |   |   |   |-- pgvecto_rs.py
|   |   |   |   |   |   |-- pgvector.py
|   |   |   |   |   |   |-- pinecone.py
|   |   |   |   |   |   |-- qdrant.py
|   |   |   |   |   |   |-- rocksetdb.py
|   |   |   |   |   |   |-- scann.py
|   |   |   |   |   |   |-- semadb.py
|   |   |   |   |   |   |-- singlestoredb.py
|   |   |   |   |   |   |-- sklearn.py
|   |   |   |   |   |   |-- sqlitevss.py
|   |   |   |   |   |   |-- starrocks.py
|   |   |   |   |   |   |-- supabase.py
|   |   |   |   |   |   |-- tair.py
|   |   |   |   |   |   |-- tencentvectordb.py
|   |   |   |   |   |   |-- tiledb.py
|   |   |   |   |   |   |-- timescalevector.py
|   |   |   |   |   |   |-- typesense.py
|   |   |   |   |   |   |-- usearch.py
|   |   |   |   |   |   |-- utils.py
|   |   |   |   |   |   |-- vald.py
|   |   |   |   |   |   |-- vearch.py
|   |   |   |   |   |   |-- vectara.py
|   |   |   |   |   |   |-- vespa.py
|   |   |   |   |   |   |-- weaviate.py
|   |   |   |   |   |   |-- xata.py
|   |   |   |   |   |   |-- yellowbrick.py
|   |   |   |   |   |   |-- zep.py
|   |   |   |   |   |   \-- zilliz.py
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- base_language.py
|   |   |   |   |   |-- base_memory.py
|   |   |   |   |   |-- cache.py
|   |   |   |   |   |-- env.py
|   |   |   |   |   |-- example_generator.py
|   |   |   |   |   |-- formatting.py
|   |   |   |   |   |-- globals.py
|   |   |   |   |   |-- hub.py
|   |   |   |   |   |-- input.py
|   |   |   |   |   |-- model_laboratory.py
|   |   |   |   |   |-- py.typed
|   |   |   |   |   |-- python.py
|   |   |   |   |   |-- requests.py
|   |   |   |   |   |-- serpapi.py
|   |   |   |   |   |-- sql_database.py
|   |   |   |   |   \-- text_splitter.py
|   |   |   |   |-- scripts
|   |   |   |   |   |-- check_imports.py
|   |   |   |   |   \-- lint_imports.sh
|   |   |   |   |-- tests
|   |   |   |   |   |-- integration_tests
|   |   |   |   |   |   |-- cache
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- fake_embeddings.py
|   |   |   |   |   |   |-- chains
|   |   |   |   |   |   |   |-- openai_functions
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- test_openapi.py
|   |   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |   |-- chat_models
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_base.py
|   |   |   |   |   |   |-- embeddings
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_base.py
|   |   |   |   |   |   |-- evaluation
|   |   |   |   |   |   |   |-- embedding_distance
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- test_embedding.py
|   |   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |   |-- examples
|   |   |   |   |   |   |   |-- brandfetch-brandfetch-2.0.0-resolved.json
|   |   |   |   |   |   |   |-- default-encoding.py
|   |   |   |   |   |   |   |-- duplicate-chars.pdf
|   |   |   |   |   |   |   |-- example-utf8.html
|   |   |   |   |   |   |   |-- example.html
|   |   |   |   |   |   |   |-- example.json
|   |   |   |   |   |   |   |-- example.mht
|   |   |   |   |   |   |   |-- facebook_chat.json
|   |   |   |   |   |   |   |-- factbook.xml
|   |   |   |   |   |   |   |-- fake-email-attachment.eml
|   |   |   |   |   |   |   |-- fake.odt
|   |   |   |   |   |   |   |-- hello.msg
|   |   |   |   |   |   |   |-- hello.pdf
|   |   |   |   |   |   |   |-- hello_world.js
|   |   |   |   |   |   |   |-- hello_world.py
|   |   |   |   |   |   |   |-- layout-parser-paper.pdf
|   |   |   |   |   |   |   |-- multi-page-forms-sample-2-page.pdf
|   |   |   |   |   |   |   |-- non-utf8-encoding.py
|   |   |   |   |   |   |   |-- README.org
|   |   |   |   |   |   |   |-- README.rst
|   |   |   |   |   |   |   |-- sample_rss_feeds.opml
|   |   |   |   |   |   |   |-- sitemap.xml
|   |   |   |   |   |   |   |-- slack_export.zip
|   |   |   |   |   |   |   |-- stanley-cups.csv
|   |   |   |   |   |   |   |-- stanley-cups.tsv
|   |   |   |   |   |   |   |-- stanley-cups.xlsx
|   |   |   |   |   |   |   \-- whatsapp_chat.txt
|   |   |   |   |   |   |-- memory
|   |   |   |   |   |   |   |-- docker-compose
|   |   |   |   |   |   |   |   \-- elasticsearch.yml
|   |   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |   |-- prompts
|   |   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |   |-- retrievers
|   |   |   |   |   |   |   \-- document_compressors
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       |-- test_cohere_reranker.py
|   |   |   |   |   |   |       \-- test_listwise_rerank.py
|   |   |   |   |   |   |-- .env.example
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_compile.py
|   |   |   |   |   |   |-- test_hub.py
|   |   |   |   |   |   \-- test_schema.py
|   |   |   |   |   |-- mock_servers
|   |   |   |   |   |   |-- robot
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- server.py
|   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |-- unit_tests
|   |   |   |   |   |   |-- _api
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_importing.py
|   |   |   |   |   |   |-- agents
|   |   |   |   |   |   |   |-- agent_toolkits
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- test_imports.py
|   |   |   |   |   |   |   |-- format_scratchpad
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- test_log.py
|   |   |   |   |   |   |   |   |-- test_log_to_messages.py
|   |   |   |   |   |   |   |   |-- test_openai_functions.py
|   |   |   |   |   |   |   |   |-- test_openai_tools.py
|   |   |   |   |   |   |   |   \-- test_xml.py
|   |   |   |   |   |   |   |-- output_parsers
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- test_convo_output_parser.py
|   |   |   |   |   |   |   |   |-- test_json.py
|   |   |   |   |   |   |   |   |-- test_openai_functions.py
|   |   |   |   |   |   |   |   |-- test_react_json_single_input.py
|   |   |   |   |   |   |   |   |-- test_react_single_input.py
|   |   |   |   |   |   |   |   |-- test_self_ask.py
|   |   |   |   |   |   |   |   \-- test_xml.py
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_agent.py
|   |   |   |   |   |   |   |-- test_agent_async.py
|   |   |   |   |   |   |   |-- test_agent_iterator.py
|   |   |   |   |   |   |   |-- test_chat.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   |-- test_initialize.py
|   |   |   |   |   |   |   |-- test_mrkl.py
|   |   |   |   |   |   |   |-- test_mrkl_output_parser.py
|   |   |   |   |   |   |   |-- test_openai_assistant.py
|   |   |   |   |   |   |   |-- test_openai_functions_multi.py
|   |   |   |   |   |   |   |-- test_public_api.py
|   |   |   |   |   |   |   |-- test_structured_chat.py
|   |   |   |   |   |   |   \-- test_types.py
|   |   |   |   |   |   |-- callbacks
|   |   |   |   |   |   |   |-- tracers
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- test_logging.py
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- fake_callback_handler.py
|   |   |   |   |   |   |   |-- test_base.py
|   |   |   |   |   |   |   |-- test_file.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   |-- test_manager.py
|   |   |   |   |   |   |   \-- test_stdout.py
|   |   |   |   |   |   |-- chains
|   |   |   |   |   |   |   |-- query_constructor
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- test_parser.py
|   |   |   |   |   |   |   |-- question_answering
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- test_map_rerank_prompt.py
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_base.py
|   |   |   |   |   |   |   |-- test_combine_documents.py
|   |   |   |   |   |   |   |-- test_constitutional_ai.py
|   |   |   |   |   |   |   |-- test_conversation.py
|   |   |   |   |   |   |   |-- test_conversation_retrieval.py
|   |   |   |   |   |   |   |-- test_flare.py
|   |   |   |   |   |   |   |-- test_history_aware_retriever.py
|   |   |   |   |   |   |   |-- test_hyde.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   |-- test_llm_checker.py
|   |   |   |   |   |   |   |-- test_llm_math.py
|   |   |   |   |   |   |   |-- test_llm_summarization_checker.py
|   |   |   |   |   |   |   |-- test_memory.py
|   |   |   |   |   |   |   |-- test_qa_with_sources.py
|   |   |   |   |   |   |   |-- test_retrieval.py
|   |   |   |   |   |   |   |-- test_sequential.py
|   |   |   |   |   |   |   |-- test_summary_buffer_memory.py
|   |   |   |   |   |   |   \-- test_transform.py
|   |   |   |   |   |   |-- chat_models
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_base.py
|   |   |   |   |   |   |   \-- test_imports.py
|   |   |   |   |   |   |-- data
|   |   |   |   |   |   |   |-- prompts
|   |   |   |   |   |   |   |   |-- prompt_extra_args.json
|   |   |   |   |   |   |   |   |-- prompt_missing_args.json
|   |   |   |   |   |   |   |   \-- simple_prompt.json
|   |   |   |   |   |   |   \-- prompt_file.txt
|   |   |   |   |   |   |-- docstore
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_imports.py
|   |   |   |   |   |   |-- document_loaders
|   |   |   |   |   |   |   |-- blob_loaders
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- test_public_api.py
|   |   |   |   |   |   |   |-- parsers
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- test_public_api.py
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_base.py
|   |   |   |   |   |   |   \-- test_imports.py
|   |   |   |   |   |   |-- document_transformers
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_imports.py
|   |   |   |   |   |   |-- embeddings
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_base.py
|   |   |   |   |   |   |   |-- test_caching.py
|   |   |   |   |   |   |   \-- test_imports.py
|   |   |   |   |   |   |-- evaluation
|   |   |   |   |   |   |   |-- agents
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- test_eval_chain.py
|   |   |   |   |   |   |   |-- comparison
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- test_eval_chain.py
|   |   |   |   |   |   |   |-- criteria
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- test_eval_chain.py
|   |   |   |   |   |   |   |-- exact_match
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- test_base.py
|   |   |   |   |   |   |   |-- parsing
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- test_base.py
|   |   |   |   |   |   |   |   |-- test_json_distance.py
|   |   |   |   |   |   |   |   \-- test_json_schema.py
|   |   |   |   |   |   |   |-- qa
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- test_eval_chain.py
|   |   |   |   |   |   |   |-- regex_match
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- test_base.py
|   |   |   |   |   |   |   |-- run_evaluators
|   |   |   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |   |   |-- scoring
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- test_eval_chain.py
|   |   |   |   |   |   |   |-- string_distance
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- test_base.py
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_imports.py
|   |   |   |   |   |   |-- examples
|   |   |   |   |   |   |   |-- test_specs
|   |   |   |   |   |   |   |   |-- apis-guru
|   |   |   |   |   |   |   |   |   \-- apispec.json
|   |   |   |   |   |   |   |   |-- biztoc
|   |   |   |   |   |   |   |   |   \-- apispec.json
|   |   |   |   |   |   |   |   |-- calculator
|   |   |   |   |   |   |   |   |   \-- apispec.json
|   |   |   |   |   |   |   |   |-- datasette
|   |   |   |   |   |   |   |   |   \-- apispec.json
|   |   |   |   |   |   |   |   |-- freetv-app
|   |   |   |   |   |   |   |   |   \-- apispec.json
|   |   |   |   |   |   |   |   |-- joinmilo
|   |   |   |   |   |   |   |   |   \-- apispec.json
|   |   |   |   |   |   |   |   |-- klarna
|   |   |   |   |   |   |   |   |   \-- apispec.json
|   |   |   |   |   |   |   |   |-- milo
|   |   |   |   |   |   |   |   |   \-- apispec.json
|   |   |   |   |   |   |   |   |-- quickchart
|   |   |   |   |   |   |   |   |   \-- apispec.json
|   |   |   |   |   |   |   |   |-- robot
|   |   |   |   |   |   |   |   |   \-- apispec.yaml
|   |   |   |   |   |   |   |   |-- schooldigger
|   |   |   |   |   |   |   |   |   \-- apispec.json
|   |   |   |   |   |   |   |   |-- shop
|   |   |   |   |   |   |   |   |   \-- apispec.json
|   |   |   |   |   |   |   |   |-- slack
|   |   |   |   |   |   |   |   |   \-- apispec.json
|   |   |   |   |   |   |   |   |-- speak
|   |   |   |   |   |   |   |   |   \-- apispec.json
|   |   |   |   |   |   |   |   |-- urlbox
|   |   |   |   |   |   |   |   |   \-- apispec.json
|   |   |   |   |   |   |   |   |-- wellknown
|   |   |   |   |   |   |   |   |   \-- apispec.json
|   |   |   |   |   |   |   |   |-- wolframalpha
|   |   |   |   |   |   |   |   |   \-- apispec.json
|   |   |   |   |   |   |   |   |-- wolframcloud
|   |   |   |   |   |   |   |   |   \-- apispec.json
|   |   |   |   |   |   |   |   |-- zapier
|   |   |   |   |   |   |   |   |   \-- apispec.json
|   |   |   |   |   |   |   |   \-- robot_openapi.yaml
|   |   |   |   |   |   |   |-- example-non-utf8.csv
|   |   |   |   |   |   |   |-- example-non-utf8.txt
|   |   |   |   |   |   |   |-- example-utf8.csv
|   |   |   |   |   |   |   \-- example-utf8.txt
|   |   |   |   |   |   |-- graphs
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_imports.py
|   |   |   |   |   |   |-- indexes
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_api.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   \-- test_indexing.py
|   |   |   |   |   |   |-- llms
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- fake_chat_model.py
|   |   |   |   |   |   |   |-- fake_llm.py
|   |   |   |   |   |   |   |-- test_base.py
|   |   |   |   |   |   |   |-- test_fake_chat_model.py
|   |   |   |   |   |   |   \-- test_imports.py
|   |   |   |   |   |   |-- load
|   |   |   |   |   |   |   |-- __snapshots__
|   |   |   |   |   |   |   |   \-- test_dump.ambr
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_dump.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   \-- test_load.py
|   |   |   |   |   |   |-- memory
|   |   |   |   |   |   |   |-- chat_message_histories
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- test_imports.py
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_combined_memory.py
|   |   |   |   |   |   |   \-- test_imports.py
|   |   |   |   |   |   |-- output_parsers
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_boolean_parser.py
|   |   |   |   |   |   |   |-- test_combining_parser.py
|   |   |   |   |   |   |   |-- test_datetime_parser.py
|   |   |   |   |   |   |   |-- test_enum_parser.py
|   |   |   |   |   |   |   |-- test_fix.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   |-- test_json.py
|   |   |   |   |   |   |   |-- test_pandas_dataframe_parser.py
|   |   |   |   |   |   |   |-- test_regex.py
|   |   |   |   |   |   |   |-- test_regex_dict.py
|   |   |   |   |   |   |   |-- test_retry.py
|   |   |   |   |   |   |   |-- test_structured_parser.py
|   |   |   |   |   |   |   \-- test_yaml_parser.py
|   |   |   |   |   |   |-- prompts
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_base.py
|   |   |   |   |   |   |   |-- test_chat.py
|   |   |   |   |   |   |   |-- test_few_shot.py
|   |   |   |   |   |   |   |-- test_few_shot_with_templates.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   |-- test_loading.py
|   |   |   |   |   |   |   \-- test_prompt.py
|   |   |   |   |   |   |-- retrievers
|   |   |   |   |   |   |   |-- document_compressors
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- test_chain_extract.py
|   |   |   |   |   |   |   |   |-- test_chain_filter.py
|   |   |   |   |   |   |   |   \-- test_listwise_rerank.py
|   |   |   |   |   |   |   |-- self_query
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- test_base.py
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- parrot_retriever.py
|   |   |   |   |   |   |   |-- sequential_retriever.py
|   |   |   |   |   |   |   |-- test_ensemble.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   |-- test_multi_query.py
|   |   |   |   |   |   |   |-- test_multi_vector.py
|   |   |   |   |   |   |   |-- test_parent_document.py
|   |   |   |   |   |   |   \-- test_time_weighted_retriever.py
|   |   |   |   |   |   |-- runnables
|   |   |   |   |   |   |   |-- __snapshots__
|   |   |   |   |   |   |   |   \-- test_openai_functions.ambr
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_hub.py
|   |   |   |   |   |   |   \-- test_openai_functions.py
|   |   |   |   |   |   |-- schema
|   |   |   |   |   |   |   |-- runnable
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- test_base.py
|   |   |   |   |   |   |   |   |-- test_branch.py
|   |   |   |   |   |   |   |   |-- test_config.py
|   |   |   |   |   |   |   |   |-- test_configurable.py
|   |   |   |   |   |   |   |   |-- test_fallbacks.py
|   |   |   |   |   |   |   |   |-- test_history.py
|   |   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   |   |-- test_passthrough.py
|   |   |   |   |   |   |   |   |-- test_retry.py
|   |   |   |   |   |   |   |   |-- test_router.py
|   |   |   |   |   |   |   |   \-- test_utils.py
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_agent.py
|   |   |   |   |   |   |   |-- test_cache.py
|   |   |   |   |   |   |   |-- test_chat.py
|   |   |   |   |   |   |   |-- test_chat_history.py
|   |   |   |   |   |   |   |-- test_document.py
|   |   |   |   |   |   |   |-- test_embeddings.py
|   |   |   |   |   |   |   |-- test_exceptions.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   |-- test_language_model.py
|   |   |   |   |   |   |   |-- test_memory.py
|   |   |   |   |   |   |   |-- test_messages.py
|   |   |   |   |   |   |   |-- test_output.py
|   |   |   |   |   |   |   |-- test_output_parser.py
|   |   |   |   |   |   |   |-- test_prompt.py
|   |   |   |   |   |   |   |-- test_prompt_template.py
|   |   |   |   |   |   |   |-- test_retriever.py
|   |   |   |   |   |   |   |-- test_storage.py
|   |   |   |   |   |   |   \-- test_vectorstore.py
|   |   |   |   |   |   |-- smith
|   |   |   |   |   |   |   |-- evaluation
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- test_runner_utils.py
|   |   |   |   |   |   |   |   \-- test_string_run_evaluator.py
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_imports.py
|   |   |   |   |   |   |-- storage
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_filesystem.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   \-- test_lc_store.py
|   |   |   |   |   |   |-- tools
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_base.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   \-- test_render.py
|   |   |   |   |   |   |-- utilities
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_imports.py
|   |   |   |   |   |   |-- utils
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   |-- test_iter.py
|   |   |   |   |   |   |   \-- test_openai_functions.py
|   |   |   |   |   |   |-- vectorstores
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_public_api.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- stubs.py
|   |   |   |   |   |   |-- test_dependencies.py
|   |   |   |   |   |   |-- test_formatting.py
|   |   |   |   |   |   |-- test_globals.py
|   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |-- test_pytest_config.py
|   |   |   |   |   |   |-- test_schema.py
|   |   |   |   |   |   \-- test_utils.py
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- data.py
|   |   |   |   |   \-- README.md
|   |   |   |   |-- .dockerignore
|   |   |   |   |-- .flake8
|   |   |   |   |-- dev.Dockerfile
|   |   |   |   |-- extended_testing_deps.txt
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   \-- uv.lock
|   |   |   |-- langchain_v1
|   |   |   |   |-- langchain
|   |   |   |   |   |-- agents
|   |   |   |   |   |   |-- middleware
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- _execution.py
|   |   |   |   |   |   |   |-- _redaction.py
|   |   |   |   |   |   |   |-- _retry.py
|   |   |   |   |   |   |   |-- context_editing.py
|   |   |   |   |   |   |   |-- file_search.py
|   |   |   |   |   |   |   |-- human_in_the_loop.py
|   |   |   |   |   |   |   |-- model_call_limit.py
|   |   |   |   |   |   |   |-- model_fallback.py
|   |   |   |   |   |   |   |-- model_retry.py
|   |   |   |   |   |   |   |-- pii.py
|   |   |   |   |   |   |   |-- shell_tool.py
|   |   |   |   |   |   |   |-- summarization.py
|   |   |   |   |   |   |   |-- todo.py
|   |   |   |   |   |   |   |-- tool_call_limit.py
|   |   |   |   |   |   |   |-- tool_emulator.py
|   |   |   |   |   |   |   |-- tool_retry.py
|   |   |   |   |   |   |   |-- tool_selection.py
|   |   |   |   |   |   |   \-- types.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- factory.py
|   |   |   |   |   |   \-- structured_output.py
|   |   |   |   |   |-- chat_models
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- base.py
|   |   |   |   |   |-- embeddings
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- base.py
|   |   |   |   |   |-- messages
|   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |-- rate_limiters
|   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |-- tools
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- tool_node.py
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- py.typed
|   |   |   |   |-- scripts
|   |   |   |   |   |-- check_imports.py
|   |   |   |   |   \-- check_version.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- cassettes
|   |   |   |   |   |   |-- test_inference_to_native_output[False].yaml.gz
|   |   |   |   |   |   |-- test_inference_to_native_output[True].yaml.gz
|   |   |   |   |   |   |-- test_inference_to_tool_output[False].yaml.gz
|   |   |   |   |   |   |-- test_inference_to_tool_output[True].yaml.gz
|   |   |   |   |   |   |-- test_strict_mode[False].yaml.gz
|   |   |   |   |   |   \-- test_strict_mode[True].yaml.gz
|   |   |   |   |   |-- integration_tests
|   |   |   |   |   |   |-- agents
|   |   |   |   |   |   |   |-- middleware
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- test_shell_tool_integration.py
|   |   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |   |-- cache
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- fake_embeddings.py
|   |   |   |   |   |   |-- chat_models
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_base.py
|   |   |   |   |   |   |-- embeddings
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_base.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   \-- test_compile.py
|   |   |   |   |   |-- unit_tests
|   |   |   |   |   |   |-- agents
|   |   |   |   |   |   |   |-- __snapshots__
|   |   |   |   |   |   |   |   |-- test_middleware_agent.ambr
|   |   |   |   |   |   |   |   |-- test_middleware_decorators.ambr
|   |   |   |   |   |   |   |   |-- test_middleware_framework.ambr
|   |   |   |   |   |   |   |   \-- test_return_direct_graph.ambr
|   |   |   |   |   |   |   |-- middleware
|   |   |   |   |   |   |   |   |-- __snapshots__
|   |   |   |   |   |   |   |   |   |-- test_middleware_decorators.ambr
|   |   |   |   |   |   |   |   |   |-- test_middleware_diagram.ambr
|   |   |   |   |   |   |   |   |   \-- test_middleware_framework.ambr
|   |   |   |   |   |   |   |   |-- core
|   |   |   |   |   |   |   |   |   |-- __snapshots__
|   |   |   |   |   |   |   |   |   |   |-- test_decorators.ambr
|   |   |   |   |   |   |   |   |   |   |-- test_diagram.ambr
|   |   |   |   |   |   |   |   |   |   \-- test_framework.ambr
|   |   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |   |-- test_composition.py
|   |   |   |   |   |   |   |   |   |-- test_decorators.py
|   |   |   |   |   |   |   |   |   |-- test_diagram.py
|   |   |   |   |   |   |   |   |   |-- test_dynamic_tools.py
|   |   |   |   |   |   |   |   |   |-- test_framework.py
|   |   |   |   |   |   |   |   |   |-- test_overrides.py
|   |   |   |   |   |   |   |   |   |-- test_sync_async_wrappers.py
|   |   |   |   |   |   |   |   |   |-- test_tools.py
|   |   |   |   |   |   |   |   |   |-- test_wrap_model_call.py
|   |   |   |   |   |   |   |   |   |-- test_wrap_model_call_state_update.py
|   |   |   |   |   |   |   |   |   \-- test_wrap_tool_call.py
|   |   |   |   |   |   |   |   |-- implementations
|   |   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |   |-- test_context_editing.py
|   |   |   |   |   |   |   |   |   |-- test_file_search.py
|   |   |   |   |   |   |   |   |   |-- test_human_in_the_loop.py
|   |   |   |   |   |   |   |   |   |-- test_model_call_limit.py
|   |   |   |   |   |   |   |   |   |-- test_model_fallback.py
|   |   |   |   |   |   |   |   |   |-- test_model_retry.py
|   |   |   |   |   |   |   |   |   |-- test_pii.py
|   |   |   |   |   |   |   |   |   |-- test_shell_execution_policies.py
|   |   |   |   |   |   |   |   |   |-- test_shell_tool.py
|   |   |   |   |   |   |   |   |   |-- test_structured_output_retry.py
|   |   |   |   |   |   |   |   |   |-- test_summarization.py
|   |   |   |   |   |   |   |   |   |-- test_todo.py
|   |   |   |   |   |   |   |   |   |-- test_tool_call_limit.py
|   |   |   |   |   |   |   |   |   |-- test_tool_emulator.py
|   |   |   |   |   |   |   |   |   |-- test_tool_retry.py
|   |   |   |   |   |   |   |   |   \-- test_tool_selection.py
|   |   |   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |   |   |-- middleware_typing
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- test_middleware_backwards_compat.py
|   |   |   |   |   |   |   |   |-- test_middleware_type_errors.py
|   |   |   |   |   |   |   |   \-- test_middleware_typing.py
|   |   |   |   |   |   |   |-- specifications
|   |   |   |   |   |   |   |   |-- responses.json
|   |   |   |   |   |   |   |   \-- return_direct.json
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- any_str.py
|   |   |   |   |   |   |   |-- compose-postgres.yml
|   |   |   |   |   |   |   |-- compose-redis.yml
|   |   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |   |-- conftest_checkpointer.py
|   |   |   |   |   |   |   |-- conftest_store.py
|   |   |   |   |   |   |   |-- memory_assert.py
|   |   |   |   |   |   |   |-- messages.py
|   |   |   |   |   |   |   |-- model.py
|   |   |   |   |   |   |   |-- test_agent_name.py
|   |   |   |   |   |   |   |-- test_create_agent_tool_validation.py
|   |   |   |   |   |   |   |-- test_fetch_last_ai_and_tool_messages.py
|   |   |   |   |   |   |   |-- test_injected_runtime_create_agent.py
|   |   |   |   |   |   |   |-- test_kwargs_tool_runtime_injection.py
|   |   |   |   |   |   |   |-- test_react_agent.py
|   |   |   |   |   |   |   |-- test_response_format.py
|   |   |   |   |   |   |   |-- test_response_format_integration.py
|   |   |   |   |   |   |   |-- test_responses.py
|   |   |   |   |   |   |   |-- test_responses_spec.py
|   |   |   |   |   |   |   |-- test_return_direct_graph.py
|   |   |   |   |   |   |   |-- test_return_direct_spec.py
|   |   |   |   |   |   |   |-- test_state_schema.py
|   |   |   |   |   |   |   |-- test_system_message.py
|   |   |   |   |   |   |   \-- utils.py
|   |   |   |   |   |   |-- chat_models
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_chat_models.py
|   |   |   |   |   |   |-- embeddings
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_base.py
|   |   |   |   |   |   |   \-- test_imports.py
|   |   |   |   |   |   |-- tools
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_imports.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_dependencies.py
|   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |-- test_pytest_config.py
|   |   |   |   |   |   \-- test_version.py
|   |   |   |   |   \-- __init__.py
|   |   |   |   |-- extended_testing_deps.txt
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   \-- uv.lock
|   |   |   |-- model-profiles
|   |   |   |   |-- langchain_model_profiles
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- cli.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- integration_tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_compile.py
|   |   |   |   |   |-- unit_tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_cli.py
|   |   |   |   |   \-- __init__.py
|   |   |   |   |-- extended_testing_deps.txt
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   \-- uv.lock
|   |   |   |-- partners
|   |   |   |   |-- anthropic
|   |   |   |   |   |-- langchain_anthropic
|   |   |   |   |   |   |-- data
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- _profiles.py
|   |   |   |   |   |   |   \-- profile_augmentations.toml
|   |   |   |   |   |   |-- middleware
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- anthropic_tools.py
|   |   |   |   |   |   |   |-- bash.py
|   |   |   |   |   |   |   |-- file_search.py
|   |   |   |   |   |   |   \-- prompt_caching.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- _client_utils.py
|   |   |   |   |   |   |-- _compat.py
|   |   |   |   |   |   |-- _version.py
|   |   |   |   |   |   |-- chat_models.py
|   |   |   |   |   |   |-- experimental.py
|   |   |   |   |   |   |-- llms.py
|   |   |   |   |   |   |-- output_parsers.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- scripts
|   |   |   |   |   |   |-- check_imports.py
|   |   |   |   |   |   |-- check_version.py
|   |   |   |   |   |   \-- lint_imports.sh
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- cassettes
|   |   |   |   |   |   |   |-- test_agent_loop.yaml.gz
|   |   |   |   |   |   |   |-- test_agent_loop_streaming.yaml.gz
|   |   |   |   |   |   |   |-- test_citations.yaml.gz
|   |   |   |   |   |   |   |-- test_code_execution.yaml.gz
|   |   |   |   |   |   |   |-- test_code_execution_old.yaml.gz
|   |   |   |   |   |   |   |-- test_compaction.yaml.gz
|   |   |   |   |   |   |   |-- test_compaction_streaming.yaml.gz
|   |   |   |   |   |   |   |-- test_context_management.yaml.gz
|   |   |   |   |   |   |   |-- test_programmatic_tool_use.yaml.gz
|   |   |   |   |   |   |   |-- test_programmatic_tool_use_streaming.yaml.gz
|   |   |   |   |   |   |   |-- test_redacted_thinking.yaml.gz
|   |   |   |   |   |   |   |-- test_remote_mcp.yaml.gz
|   |   |   |   |   |   |   |-- test_response_format_in_agent.yaml.gz
|   |   |   |   |   |   |   |-- test_search_result_tool_message.yaml.gz
|   |   |   |   |   |   |   |-- test_strict_tool_use.yaml.gz
|   |   |   |   |   |   |   |-- test_thinking.yaml.gz
|   |   |   |   |   |   |   |-- test_tool_search.yaml.gz
|   |   |   |   |   |   |   |-- test_web_fetch.yaml.gz
|   |   |   |   |   |   |   |-- test_web_fetch_v1.yaml.gz
|   |   |   |   |   |   |   |-- test_web_search.yaml.gz
|   |   |   |   |   |   |   \-- TestAnthropicStandard.test_stream_time.yaml.gz
|   |   |   |   |   |   |-- integration_tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_chat_models.py
|   |   |   |   |   |   |   |-- test_compile.py
|   |   |   |   |   |   |   |-- test_llms.py
|   |   |   |   |   |   |   \-- test_standard.py
|   |   |   |   |   |   |-- unit_tests
|   |   |   |   |   |   |   |-- __snapshots__
|   |   |   |   |   |   |   |   \-- test_standard.ambr
|   |   |   |   |   |   |   |-- middleware
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- test_anthropic_tools.py
|   |   |   |   |   |   |   |   |-- test_bash.py
|   |   |   |   |   |   |   |   |-- test_file_search.py
|   |   |   |   |   |   |   |   \-- test_prompt_caching.py
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- _utils.py
|   |   |   |   |   |   |   |-- test_chat_models.py
|   |   |   |   |   |   |   |-- test_client_utils.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   |-- test_llms.py
|   |   |   |   |   |   |   |-- test_output_parsers.py
|   |   |   |   |   |   |   \-- test_standard.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- conftest.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- chroma
|   |   |   |   |   |-- langchain_chroma
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- py.typed
|   |   |   |   |   |   \-- vectorstores.py
|   |   |   |   |   |-- scripts
|   |   |   |   |   |   |-- check_imports.py
|   |   |   |   |   |   \-- lint_imports.sh
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- integration_tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- fake_embeddings.py
|   |   |   |   |   |   |   |-- test_compile.py
|   |   |   |   |   |   |   \-- test_vectorstores.py
|   |   |   |   |   |   |-- unit_tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   |-- test_standard.py
|   |   |   |   |   |   |   \-- test_vectorstores.py
|   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- deepseek
|   |   |   |   |   |-- langchain_deepseek
|   |   |   |   |   |   |-- data
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- _profiles.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- chat_models.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- scripts
|   |   |   |   |   |   |-- check_imports.py
|   |   |   |   |   |   \-- lint_imports.sh
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- integration_tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_chat_models.py
|   |   |   |   |   |   |   \-- test_compile.py
|   |   |   |   |   |   |-- unit_tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_chat_models.py
|   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- exa
|   |   |   |   |   |-- langchain_exa
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- _utilities.py
|   |   |   |   |   |   |-- py.typed
|   |   |   |   |   |   |-- retrievers.py
|   |   |   |   |   |   \-- tools.py
|   |   |   |   |   |-- scripts
|   |   |   |   |   |   |-- check_imports.py
|   |   |   |   |   |   \-- lint_imports.sh
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- integration_tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_compile.py
|   |   |   |   |   |   |   |-- test_find_similar_tool.py
|   |   |   |   |   |   |   |-- test_retriever.py
|   |   |   |   |   |   |   \-- test_search_tool.py
|   |   |   |   |   |   |-- unit_tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   \-- test_standard.py
|   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- fireworks
|   |   |   |   |   |-- langchain_fireworks
|   |   |   |   |   |   |-- data
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- _profiles.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- _compat.py
|   |   |   |   |   |   |-- chat_models.py
|   |   |   |   |   |   |-- embeddings.py
|   |   |   |   |   |   |-- llms.py
|   |   |   |   |   |   |-- py.typed
|   |   |   |   |   |   \-- version.py
|   |   |   |   |   |-- scripts
|   |   |   |   |   |   |-- check_imports.py
|   |   |   |   |   |   \-- lint_imports.sh
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- integration_tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_chat_models.py
|   |   |   |   |   |   |   |-- test_compile.py
|   |   |   |   |   |   |   |-- test_embeddings.py
|   |   |   |   |   |   |   |-- test_llms.py
|   |   |   |   |   |   |   \-- test_standard.py
|   |   |   |   |   |   |-- unit_tests
|   |   |   |   |   |   |   |-- __snapshots__
|   |   |   |   |   |   |   |   \-- test_standard.ambr
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_chat_models.py
|   |   |   |   |   |   |   |-- test_embeddings.py
|   |   |   |   |   |   |   |-- test_embeddings_standard.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   |-- test_llms.py
|   |   |   |   |   |   |   \-- test_standard.py
|   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- groq
|   |   |   |   |   |-- langchain_groq
|   |   |   |   |   |   |-- data
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- _profiles.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- _compat.py
|   |   |   |   |   |   |-- chat_models.py
|   |   |   |   |   |   |-- py.typed
|   |   |   |   |   |   \-- version.py
|   |   |   |   |   |-- scripts
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- check_imports.py
|   |   |   |   |   |   \-- lint_imports.sh
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- cassettes
|   |   |   |   |   |   |   |-- test_code_interpreter.yaml.gz
|   |   |   |   |   |   |   \-- test_web_search.yaml.gz
|   |   |   |   |   |   |-- integration_tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_chat_models.py
|   |   |   |   |   |   |   |-- test_compile.py
|   |   |   |   |   |   |   \-- test_standard.py
|   |   |   |   |   |   |-- unit_tests
|   |   |   |   |   |   |   |-- __snapshots__
|   |   |   |   |   |   |   |   \-- test_standard.ambr
|   |   |   |   |   |   |   |-- fake
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- callbacks.py
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_chat_models.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   \-- test_standard.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- conftest.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- huggingface
|   |   |   |   |   |-- langchain_huggingface
|   |   |   |   |   |   |-- chat_models
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- huggingface.py
|   |   |   |   |   |   |-- data
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- _profiles.py
|   |   |   |   |   |   |-- embeddings
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- huggingface.py
|   |   |   |   |   |   |   \-- huggingface_endpoint.py
|   |   |   |   |   |   |-- llms
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- huggingface_endpoint.py
|   |   |   |   |   |   |   \-- huggingface_pipeline.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- integration_tests
|   |   |   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |   |-- utils
|   |   |   |   |   |   |   \-- import_utils.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- scripts
|   |   |   |   |   |   |-- check_imports.py
|   |   |   |   |   |   \-- lint_imports.sh
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- integration_tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_chat_models.py
|   |   |   |   |   |   |   |-- test_compile.py
|   |   |   |   |   |   |   |-- test_embeddings_standard.py
|   |   |   |   |   |   |   |-- test_llms.py
|   |   |   |   |   |   |   \-- test_standard.py
|   |   |   |   |   |   \-- unit_tests
|   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |       |-- test_chat_models.py
|   |   |   |   |   |       \-- test_huggingface_pipeline.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- mistralai
|   |   |   |   |   |-- langchain_mistralai
|   |   |   |   |   |   |-- data
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- _profiles.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- _compat.py
|   |   |   |   |   |   |-- chat_models.py
|   |   |   |   |   |   |-- embeddings.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- scripts
|   |   |   |   |   |   |-- check_imports.py
|   |   |   |   |   |   \-- lint_imports.sh
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- integration_tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_chat_models.py
|   |   |   |   |   |   |   |-- test_compile.py
|   |   |   |   |   |   |   |-- test_embeddings.py
|   |   |   |   |   |   |   \-- test_standard.py
|   |   |   |   |   |   |-- unit_tests
|   |   |   |   |   |   |   |-- __snapshots__
|   |   |   |   |   |   |   |   \-- test_standard.ambr
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_chat_models.py
|   |   |   |   |   |   |   |-- test_embeddings.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   \-- test_standard.py
|   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- nomic
|   |   |   |   |   |-- langchain_nomic
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- embeddings.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- scripts
|   |   |   |   |   |   |-- check_imports.py
|   |   |   |   |   |   \-- lint_imports.sh
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- integration_tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_compile.py
|   |   |   |   |   |   |   \-- test_embeddings.py
|   |   |   |   |   |   |-- unit_tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_embeddings.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   \-- test_standard.py
|   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- ollama
|   |   |   |   |   |-- langchain_ollama
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- _compat.py
|   |   |   |   |   |   |-- _utils.py
|   |   |   |   |   |   |-- chat_models.py
|   |   |   |   |   |   |-- embeddings.py
|   |   |   |   |   |   |-- llms.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- scripts
|   |   |   |   |   |   |-- check_imports.py
|   |   |   |   |   |   \-- lint_imports.sh
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- integration_tests
|   |   |   |   |   |   |   |-- chat_models
|   |   |   |   |   |   |   |   |-- cassettes
|   |   |   |   |   |   |   |   |   \-- test_chat_models_standard
|   |   |   |   |   |   |   |   |       \-- TestChatOllama.test_stream_time.yaml
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- test_chat_models.py
|   |   |   |   |   |   |   |   |-- test_chat_models_reasoning.py
|   |   |   |   |   |   |   |   \-- test_chat_models_standard.py
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_compile.py
|   |   |   |   |   |   |   |-- test_embeddings.py
|   |   |   |   |   |   |   \-- test_llms.py
|   |   |   |   |   |   |-- unit_tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_auth.py
|   |   |   |   |   |   |   |-- test_chat_models.py
|   |   |   |   |   |   |   |-- test_embeddings.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   \-- test_llms.py
|   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- openai
|   |   |   |   |   |-- langchain_openai
|   |   |   |   |   |   |-- chat_models
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- _client_utils.py
|   |   |   |   |   |   |   |-- _compat.py
|   |   |   |   |   |   |   |-- azure.py
|   |   |   |   |   |   |   \-- base.py
|   |   |   |   |   |   |-- data
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- _profiles.py
|   |   |   |   |   |   |   \-- profile_augmentations.toml
|   |   |   |   |   |   |-- embeddings
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- azure.py
|   |   |   |   |   |   |   \-- base.py
|   |   |   |   |   |   |-- llms
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- azure.py
|   |   |   |   |   |   |   \-- base.py
|   |   |   |   |   |   |-- middleware
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- openai_moderation.py
|   |   |   |   |   |   |-- output_parsers
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- tools.py
|   |   |   |   |   |   |-- tools
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- custom_tool.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- scripts
|   |   |   |   |   |   |-- check_imports.py
|   |   |   |   |   |   \-- lint_imports.sh
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- cassettes
|   |   |   |   |   |   |   |-- test_code_interpreter.yaml.gz
|   |   |   |   |   |   |   |-- test_compaction.yaml.gz
|   |   |   |   |   |   |   |-- test_compaction_streaming.yaml.gz
|   |   |   |   |   |   |   |-- test_custom_tool.yaml.gz
|   |   |   |   |   |   |   |-- test_file_search.yaml.gz
|   |   |   |   |   |   |   |-- test_function_calling.yaml.gz
|   |   |   |   |   |   |   |-- test_image_generation_multi_turn.yaml.gz
|   |   |   |   |   |   |   |-- test_image_generation_streaming.yaml.gz
|   |   |   |   |   |   |   |-- test_incomplete_response.yaml.gz
|   |   |   |   |   |   |   |-- test_mcp_builtin.yaml.gz
|   |   |   |   |   |   |   |-- test_mcp_builtin_zdr.yaml.gz
|   |   |   |   |   |   |   |-- test_parsed_pydantic_schema.yaml.gz
|   |   |   |   |   |   |   |-- test_reasoning.yaml.gz
|   |   |   |   |   |   |   |-- test_schema_parsing_failures.yaml.gz
|   |   |   |   |   |   |   |-- test_schema_parsing_failures_async.yaml.gz
|   |   |   |   |   |   |   |-- test_schema_parsing_failures_responses_api.yaml.gz
|   |   |   |   |   |   |   |-- test_schema_parsing_failures_responses_api_async.yaml.gz
|   |   |   |   |   |   |   |-- test_stream_reasoning_summary.yaml.gz
|   |   |   |   |   |   |   |-- test_web_search.yaml.gz
|   |   |   |   |   |   |   |-- TestOpenAIResponses.test_stream_time.yaml.gz
|   |   |   |   |   |   |   \-- TestOpenAIStandard.test_stream_time.yaml.gz
|   |   |   |   |   |   |-- integration_tests
|   |   |   |   |   |   |   |-- chat_models
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- audio_input.wav
|   |   |   |   |   |   |   |   |-- test_azure.py
|   |   |   |   |   |   |   |   |-- test_azure_standard.py
|   |   |   |   |   |   |   |   |-- test_base.py
|   |   |   |   |   |   |   |   |-- test_base_standard.py
|   |   |   |   |   |   |   |   |-- test_responses_api.py
|   |   |   |   |   |   |   |   \-- test_responses_standard.py
|   |   |   |   |   |   |   |-- embeddings
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- test_azure.py
|   |   |   |   |   |   |   |   |-- test_base.py
|   |   |   |   |   |   |   |   \-- test_base_standard.py
|   |   |   |   |   |   |   |-- llms
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- test_azure.py
|   |   |   |   |   |   |   |   \-- test_base.py
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_compile.py
|   |   |   |   |   |   |-- unit_tests
|   |   |   |   |   |   |   |-- chat_models
|   |   |   |   |   |   |   |   |-- __snapshots__
|   |   |   |   |   |   |   |   |   |-- test_azure_standard.ambr
|   |   |   |   |   |   |   |   |   |-- test_base_standard.ambr
|   |   |   |   |   |   |   |   |   \-- test_responses_standard.ambr
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- test_azure.py
|   |   |   |   |   |   |   |   |-- test_azure_standard.py
|   |   |   |   |   |   |   |   |-- test_base.py
|   |   |   |   |   |   |   |   |-- test_base_standard.py
|   |   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   |   |-- test_prompt_cache_key.py
|   |   |   |   |   |   |   |   |-- test_responses_standard.py
|   |   |   |   |   |   |   |   \-- test_responses_stream.py
|   |   |   |   |   |   |   |-- embeddings
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- test_azure_embeddings.py
|   |   |   |   |   |   |   |   |-- test_azure_standard.py
|   |   |   |   |   |   |   |   |-- test_base.py
|   |   |   |   |   |   |   |   |-- test_base_standard.py
|   |   |   |   |   |   |   |   \-- test_imports.py
|   |   |   |   |   |   |   |-- fake
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- callbacks.py
|   |   |   |   |   |   |   |-- llms
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- test_azure.py
|   |   |   |   |   |   |   |   |-- test_base.py
|   |   |   |   |   |   |   |   \-- test_imports.py
|   |   |   |   |   |   |   |-- middleware
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- test_openai_moderation_middleware.py
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   |-- test_load.py
|   |   |   |   |   |   |   |-- test_secrets.py
|   |   |   |   |   |   |   |-- test_token_counts.py
|   |   |   |   |   |   |   \-- test_tools.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- conftest.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- openrouter
|   |   |   |   |   |-- langchain_openrouter
|   |   |   |   |   |   |-- data
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- _profiles.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- chat_models.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- scripts
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- check_imports.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- integration_tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_chat_models.py
|   |   |   |   |   |   |   |-- test_compile.py
|   |   |   |   |   |   |   \-- test_standard.py
|   |   |   |   |   |   |-- unit_tests
|   |   |   |   |   |   |   |-- __snapshots__
|   |   |   |   |   |   |   |   \-- test_standard.ambr
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_chat_models.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   \-- test_standard.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- conftest.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- perplexity
|   |   |   |   |   |-- langchain_perplexity
|   |   |   |   |   |   |-- data
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- _profiles.py
|   |   |   |   |   |   |   \-- profile_augmentations.toml
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- _utils.py
|   |   |   |   |   |   |-- chat_models.py
|   |   |   |   |   |   |-- output_parsers.py
|   |   |   |   |   |   |-- py.typed
|   |   |   |   |   |   |-- retrievers.py
|   |   |   |   |   |   |-- tools.py
|   |   |   |   |   |   \-- types.py
|   |   |   |   |   |-- scripts
|   |   |   |   |   |   |-- check_imports.py
|   |   |   |   |   |   \-- lint_imports.sh
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- integration_tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_chat_models.py
|   |   |   |   |   |   |   |-- test_chat_models_standard.py
|   |   |   |   |   |   |   |-- test_compile.py
|   |   |   |   |   |   |   \-- test_search_api.py
|   |   |   |   |   |   |-- unit_tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_chat_models.py
|   |   |   |   |   |   |   |-- test_chat_models_standard.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   |-- test_output_parsers.py
|   |   |   |   |   |   |   |-- test_retrievers.py
|   |   |   |   |   |   |   |-- test_secrets.py
|   |   |   |   |   |   |   \-- test_tools.py
|   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- qdrant
|   |   |   |   |   |-- langchain_qdrant
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- _utils.py
|   |   |   |   |   |   |-- fastembed_sparse.py
|   |   |   |   |   |   |-- py.typed
|   |   |   |   |   |   |-- qdrant.py
|   |   |   |   |   |   |-- sparse_embeddings.py
|   |   |   |   |   |   \-- vectorstores.py
|   |   |   |   |   |-- scripts
|   |   |   |   |   |   |-- check_imports.py
|   |   |   |   |   |   \-- lint_imports.sh
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- integration_tests
|   |   |   |   |   |   |   |-- async_api
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- test_add_texts.py
|   |   |   |   |   |   |   |   |-- test_from_texts.py
|   |   |   |   |   |   |   |   |-- test_max_marginal_relevance.py
|   |   |   |   |   |   |   |   \-- test_similarity_search.py
|   |   |   |   |   |   |   |-- fastembed
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   \-- test_fastembed_sparse.py
|   |   |   |   |   |   |   |-- qdrant_vector_store
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- test_add_texts.py
|   |   |   |   |   |   |   |   |-- test_from_existing.py
|   |   |   |   |   |   |   |   |-- test_from_texts.py
|   |   |   |   |   |   |   |   |-- test_mmr.py
|   |   |   |   |   |   |   |   \-- test_search.py
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- common.py
|   |   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |   |-- fixtures.py
|   |   |   |   |   |   |   |-- test_add_texts.py
|   |   |   |   |   |   |   |-- test_compile.py
|   |   |   |   |   |   |   |-- test_embedding_interface.py
|   |   |   |   |   |   |   |-- test_from_existing_collection.py
|   |   |   |   |   |   |   |-- test_from_texts.py
|   |   |   |   |   |   |   |-- test_max_marginal_relevance.py
|   |   |   |   |   |   |   \-- test_similarity_search.py
|   |   |   |   |   |   |-- unit_tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   |-- test_standard.py
|   |   |   |   |   |   |   \-- test_vectorstores.py
|   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- xai
|   |   |   |   |   |-- langchain_xai
|   |   |   |   |   |   |-- data
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- _profiles.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- chat_models.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- scripts
|   |   |   |   |   |   |-- check_imports.py
|   |   |   |   |   |   \-- lint_imports.sh
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- integration_tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_chat_models.py
|   |   |   |   |   |   |   |-- test_chat_models_standard.py
|   |   |   |   |   |   |   \-- test_compile.py
|   |   |   |   |   |   |-- unit_tests
|   |   |   |   |   |   |   |-- __snapshots__
|   |   |   |   |   |   |   |   \-- test_chat_models_standard.ambr
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_chat_models.py
|   |   |   |   |   |   |   |-- test_chat_models_standard.py
|   |   |   |   |   |   |   |-- test_imports.py
|   |   |   |   |   |   |   \-- test_secrets.py
|   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   \-- README.md
|   |   |   |-- standard-tests
|   |   |   |   |-- langchain_tests
|   |   |   |   |   |-- integration_tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- base_store.py
|   |   |   |   |   |   |-- cache.py
|   |   |   |   |   |   |-- chat_models.py
|   |   |   |   |   |   |-- embeddings.py
|   |   |   |   |   |   |-- indexer.py
|   |   |   |   |   |   |-- retrievers.py
|   |   |   |   |   |   |-- sandboxes.py
|   |   |   |   |   |   |-- tools.py
|   |   |   |   |   |   \-- vectorstores.py
|   |   |   |   |   |-- unit_tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- chat_models.py
|   |   |   |   |   |   |-- embeddings.py
|   |   |   |   |   |   \-- tools.py
|   |   |   |   |   |-- utils
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- pydantic.py
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- base.py
|   |   |   |   |   |-- conftest.py
|   |   |   |   |   \-- py.typed
|   |   |   |   |-- scripts
|   |   |   |   |   |-- check_imports.py
|   |   |   |   |   \-- lint_imports.sh
|   |   |   |   |-- tests
|   |   |   |   |   |-- integration_tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_compile.py
|   |   |   |   |   |-- unit_tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- custom_chat_model.py
|   |   |   |   |   |   |-- test_basic_retriever.py
|   |   |   |   |   |   |-- test_basic_tool.py
|   |   |   |   |   |   |-- test_custom_chat_model.py
|   |   |   |   |   |   |-- test_decorated_tool.py
|   |   |   |   |   |   |-- test_embeddings.py
|   |   |   |   |   |   |-- test_in_memory_base_store.py
|   |   |   |   |   |   |-- test_in_memory_cache.py
|   |   |   |   |   |   \-- test_in_memory_vectorstore.py
|   |   |   |   |   \-- __init__.py
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   \-- uv.lock
|   |   |   |-- text-splitters
|   |   |   |   |-- langchain_text_splitters
|   |   |   |   |   |-- xsl
|   |   |   |   |   |   \-- converting_to_header.xslt
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- base.py
|   |   |   |   |   |-- character.py
|   |   |   |   |   |-- html.py
|   |   |   |   |   |-- json.py
|   |   |   |   |   |-- jsx.py
|   |   |   |   |   |-- konlpy.py
|   |   |   |   |   |-- latex.py
|   |   |   |   |   |-- markdown.py
|   |   |   |   |   |-- nltk.py
|   |   |   |   |   |-- py.typed
|   |   |   |   |   |-- python.py
|   |   |   |   |   |-- sentence_transformers.py
|   |   |   |   |   \-- spacy.py
|   |   |   |   |-- scripts
|   |   |   |   |   |-- check_imports.py
|   |   |   |   |   \-- lint_imports.sh
|   |   |   |   |-- tests
|   |   |   |   |   |-- integration_tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_compile.py
|   |   |   |   |   |   |-- test_nlp_text_splitters.py
|   |   |   |   |   |   \-- test_text_splitter.py
|   |   |   |   |   |-- test_data
|   |   |   |   |   |   \-- test_splitter.xslt
|   |   |   |   |   |-- unit_tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_html_security.py
|   |   |   |   |   |   \-- test_text_splitters.py
|   |   |   |   |   \-- __init__.py
|   |   |   |   |-- extended_testing_deps.txt
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   \-- uv.lock
|   |   |   |-- Makefile
|   |   |   \-- README.md
|   |   |-- .dockerignore
|   |   |-- .editorconfig
|   |   |-- .gitattributes
|   |   |-- .gitignore
|   |   |-- .markdownlint.json
|   |   |-- .mcp.json
|   |   |-- .pre-commit-config.yaml
|   |   |-- AGENTS.md
|   |   |-- CITATION.cff
|   |   |-- CLAUDE.md
|   |   |-- CONTRIBUTING.md
|   |   |-- LICENSE
|   |   \-- README.md
|   |-- llama_index
|   |   |-- .github
|   |   |   |-- ISSUE_TEMPLATE
|   |   |   |   |-- config.yml
|   |   |   |   |-- docs-form.yml
|   |   |   |   |-- feature-form.yml
|   |   |   |   |-- issue-form.yml
|   |   |   |   \-- question-form.yml
|   |   |   |-- workflows
|   |   |   |   |-- build_package.yml
|   |   |   |   |-- codeql.yml
|   |   |   |   |-- core-typecheck.yml
|   |   |   |   |-- coverage_check.yml
|   |   |   |   |-- deploy-developer-hub.yml
|   |   |   |   |-- issue_classifier.yml
|   |   |   |   |-- lint.yml
|   |   |   |   |-- llama_dev_tests.yml
|   |   |   |   |-- pre_release.yml
|   |   |   |   |-- publish_sub_package.yml
|   |   |   |   |-- release.yml
|   |   |   |   |-- stale_bot.yml
|   |   |   |   \-- unit_test.yml
|   |   |   |-- dependabot.yml
|   |   |   \-- pull_request_template.md
|   |   |-- docs
|   |   |   |-- api_reference
|   |   |   |   |-- api_reference
|   |   |   |   |   |-- _static
|   |   |   |   |   |   \-- assets
|   |   |   |   |   |       |-- LlamaLogoBrowserTab.png
|   |   |   |   |   |       \-- LlamaSquareBlack.svg
|   |   |   |   |   |-- agent
|   |   |   |   |   |   \-- index.md
|   |   |   |   |   |-- callbacks
|   |   |   |   |   |   |-- agentops.md
|   |   |   |   |   |   |-- aim.md
|   |   |   |   |   |   |-- argilla.md
|   |   |   |   |   |   |-- arize_phoenix.md
|   |   |   |   |   |   |-- honeyhive.md
|   |   |   |   |   |   |-- index.md
|   |   |   |   |   |   |-- langfuse.md
|   |   |   |   |   |   |-- literalai.md
|   |   |   |   |   |   |-- llama_debug.md
|   |   |   |   |   |   |-- openinference.md
|   |   |   |   |   |   |-- opik.md
|   |   |   |   |   |   |-- promptlayer.md
|   |   |   |   |   |   |-- token_counter.md
|   |   |   |   |   |   |-- uptrain.md
|   |   |   |   |   |   \-- wandb.md
|   |   |   |   |   |-- chat_engines
|   |   |   |   |   |   |-- condense_plus_context.md
|   |   |   |   |   |   |-- condense_question.md
|   |   |   |   |   |   |-- context.md
|   |   |   |   |   |   |-- index.md
|   |   |   |   |   |   \-- simple.md
|   |   |   |   |   |-- embeddings
|   |   |   |   |   |   |-- adapter.md
|   |   |   |   |   |   |-- alephalpha.md
|   |   |   |   |   |   |-- alibabacloud_aisearch.md
|   |   |   |   |   |   |-- anyscale.md
|   |   |   |   |   |   |-- autoembeddings.md
|   |   |   |   |   |   |-- azure_inference.md
|   |   |   |   |   |   |-- azure_openai.md
|   |   |   |   |   |   |-- baseten.md
|   |   |   |   |   |   |-- bedrock.md
|   |   |   |   |   |   |-- clarifai.md
|   |   |   |   |   |   |-- clip.md
|   |   |   |   |   |   |-- cloudflare_workersai.md
|   |   |   |   |   |   |-- cohere.md
|   |   |   |   |   |   |-- dashscope.md
|   |   |   |   |   |   |-- databricks.md
|   |   |   |   |   |   |-- deepinfra.md
|   |   |   |   |   |   |-- elasticsearch.md
|   |   |   |   |   |   |-- fastembed.md
|   |   |   |   |   |   |-- fireworks.md
|   |   |   |   |   |   |-- gaudi.md
|   |   |   |   |   |   |-- gigachat.md
|   |   |   |   |   |   |-- google_genai.md
|   |   |   |   |   |   |-- heroku.md
|   |   |   |   |   |   |-- huggingface.md
|   |   |   |   |   |   |-- huggingface_api.md
|   |   |   |   |   |   |-- huggingface_openvino.md
|   |   |   |   |   |   |-- huggingface_optimum.md
|   |   |   |   |   |   |-- huggingface_optimum_intel.md
|   |   |   |   |   |   |-- ibm.md
|   |   |   |   |   |   |-- index.md
|   |   |   |   |   |   |-- instructor.md
|   |   |   |   |   |   |-- ipex_llm.md
|   |   |   |   |   |   |-- isaacus.md
|   |   |   |   |   |   |-- jinaai.md
|   |   |   |   |   |   |-- langchain.md
|   |   |   |   |   |   |-- litellm.md
|   |   |   |   |   |   |-- llamafile.md
|   |   |   |   |   |   |-- llm_rails.md
|   |   |   |   |   |   |-- mistralai.md
|   |   |   |   |   |   |-- mixedbreadai.md
|   |   |   |   |   |   |-- modelscope.md
|   |   |   |   |   |   |-- nebius.md
|   |   |   |   |   |   |-- netmind.md
|   |   |   |   |   |   |-- nomic.md
|   |   |   |   |   |   |-- nvidia.md
|   |   |   |   |   |   |-- oci_data_science.md
|   |   |   |   |   |   |-- oci_genai.md
|   |   |   |   |   |   |-- ollama.md
|   |   |   |   |   |   |-- opea.md
|   |   |   |   |   |   |-- openai.md
|   |   |   |   |   |   |-- openai_like.md
|   |   |   |   |   |   |-- openvino_genai.md
|   |   |   |   |   |   |-- oracleai.md
|   |   |   |   |   |   |-- premai.md
|   |   |   |   |   |   |-- sagemaker_endpoint.md
|   |   |   |   |   |   |-- siliconflow.md
|   |   |   |   |   |   |-- text_embeddings_inference.md
|   |   |   |   |   |   |-- textembed.md
|   |   |   |   |   |   |-- together.md
|   |   |   |   |   |   |-- upstage.md
|   |   |   |   |   |   |-- vertex.md
|   |   |   |   |   |   |-- vertex_endpoint.md
|   |   |   |   |   |   |-- vllm.md
|   |   |   |   |   |   |-- voyageai.md
|   |   |   |   |   |   |-- xinference.md
|   |   |   |   |   |   |-- yandexgpt.md
|   |   |   |   |   |   \-- zhipuai.md
|   |   |   |   |   |-- evaluation
|   |   |   |   |   |   |-- answer_relevancy.md
|   |   |   |   |   |   |-- context_relevancy.md
|   |   |   |   |   |   |-- correctness.md
|   |   |   |   |   |   |-- dataset_generation.md
|   |   |   |   |   |   |-- faithfullness.md
|   |   |   |   |   |   |-- guideline.md
|   |   |   |   |   |   |-- index.md
|   |   |   |   |   |   |-- metrics.md
|   |   |   |   |   |   |-- multi_modal.md
|   |   |   |   |   |   |-- pairwise_comparison.md
|   |   |   |   |   |   |-- query_response.md
|   |   |   |   |   |   |-- response.md
|   |   |   |   |   |   |-- retrieval.md
|   |   |   |   |   |   |-- semantic_similarity.md
|   |   |   |   |   |   \-- tonic_validate.md
|   |   |   |   |   |-- extractors
|   |   |   |   |   |   |-- documentcontext.md
|   |   |   |   |   |   |-- entity.md
|   |   |   |   |   |   |-- index.md
|   |   |   |   |   |   |-- keyword.md
|   |   |   |   |   |   |-- marvin.md
|   |   |   |   |   |   |-- pydantic.md
|   |   |   |   |   |   |-- question.md
|   |   |   |   |   |   |-- relik.md
|   |   |   |   |   |   |-- summary.md
|   |   |   |   |   |   \-- title.md
|   |   |   |   |   |-- graph_rag
|   |   |   |   |   |   \-- cognee.md
|   |   |   |   |   |-- indices
|   |   |   |   |   |   |-- bge_m3.md
|   |   |   |   |   |   |-- colbert.md
|   |   |   |   |   |   |-- dashscope.md
|   |   |   |   |   |   |-- document_summary.md
|   |   |   |   |   |   |-- google.md
|   |   |   |   |   |   |-- index.md
|   |   |   |   |   |   |-- keyword.md
|   |   |   |   |   |   |-- knowledge_graph.md
|   |   |   |   |   |   |-- lancedb.md
|   |   |   |   |   |   |-- llama_cloud.md
|   |   |   |   |   |   |-- postgresml.md
|   |   |   |   |   |   |-- property_graph.md
|   |   |   |   |   |   |-- summary.md
|   |   |   |   |   |   |-- tree.md
|   |   |   |   |   |   |-- vectara.md
|   |   |   |   |   |   |-- vector.md
|   |   |   |   |   |   \-- vertexai.md
|   |   |   |   |   |-- ingestion
|   |   |   |   |   |   |-- index.md
|   |   |   |   |   |   \-- ray.md
|   |   |   |   |   |-- instrumentation
|   |   |   |   |   |   |-- event_handlers.md
|   |   |   |   |   |   |-- event_types.md
|   |   |   |   |   |   |-- index.md
|   |   |   |   |   |   |-- span_handlers.md
|   |   |   |   |   |   \-- span_types.md
|   |   |   |   |   |-- llama_dataset
|   |   |   |   |   |   \-- index.md
|   |   |   |   |   |-- llama_deploy
|   |   |   |   |   |   \-- README.txt
|   |   |   |   |   |-- llms
|   |   |   |   |   |   |-- ai21.md
|   |   |   |   |   |   |-- aibadgr.md
|   |   |   |   |   |   |-- alephalpha.md
|   |   |   |   |   |   |-- alibabacloud_aisearch.md
|   |   |   |   |   |   |-- anthropic.md
|   |   |   |   |   |   |-- anyscale.md
|   |   |   |   |   |   |-- apertis.md
|   |   |   |   |   |   |-- asi.md
|   |   |   |   |   |   |-- azure_inference.md
|   |   |   |   |   |   |-- azure_openai.md
|   |   |   |   |   |   |-- baseten.md
|   |   |   |   |   |   |-- bedrock.md
|   |   |   |   |   |   |-- bedrock_converse.md
|   |   |   |   |   |   |-- cerebras.md
|   |   |   |   |   |   |-- clarifai.md
|   |   |   |   |   |   |-- cleanlab.md
|   |   |   |   |   |   |-- cloudflare_ai_gateway.md
|   |   |   |   |   |   |-- cohere.md
|   |   |   |   |   |   |-- cometapi.md
|   |   |   |   |   |   |-- contextual.md
|   |   |   |   |   |   |-- cortex.md
|   |   |   |   |   |   |-- custom_llm.md
|   |   |   |   |   |   |-- dashscope.md
|   |   |   |   |   |   |-- databricks.md
|   |   |   |   |   |   |-- deepinfra.md
|   |   |   |   |   |   |-- deepseek.md
|   |   |   |   |   |   |-- everlyai.md
|   |   |   |   |   |   |-- featherlessai.md
|   |   |   |   |   |   |-- fireworks.md
|   |   |   |   |   |   |-- friendli.md
|   |   |   |   |   |   |-- gaudi.md
|   |   |   |   |   |   |-- gigachat.md
|   |   |   |   |   |   |-- google_genai.md
|   |   |   |   |   |   |-- groq.md
|   |   |   |   |   |   |-- helicone.md
|   |   |   |   |   |   |-- heroku.md
|   |   |   |   |   |   |-- huggingface.md
|   |   |   |   |   |   |-- huggingface_api.md
|   |   |   |   |   |   |-- ibm.md
|   |   |   |   |   |   |-- index.md
|   |   |   |   |   |   |-- ipex_llm.md
|   |   |   |   |   |   |-- keywordsai.md
|   |   |   |   |   |   |-- konko.md
|   |   |   |   |   |   |-- langchain.md
|   |   |   |   |   |   |-- litellm.md
|   |   |   |   |   |   |-- llama_api.md
|   |   |   |   |   |   |-- llama_cpp.md
|   |   |   |   |   |   |-- llamafile.md
|   |   |   |   |   |   |-- lmstudio.md
|   |   |   |   |   |   |-- localai.md
|   |   |   |   |   |   |-- maritalk.md
|   |   |   |   |   |   |-- meta.md
|   |   |   |   |   |   |-- mistral_rs.md
|   |   |   |   |   |   |-- mistralai.md
|   |   |   |   |   |   |-- mlx.md
|   |   |   |   |   |   |-- modelscope.md
|   |   |   |   |   |   |-- monsterapi.md
|   |   |   |   |   |   |-- mymagic.md
|   |   |   |   |   |   |-- nebius.md
|   |   |   |   |   |   |-- netmind.md
|   |   |   |   |   |   |-- neutrino.md
|   |   |   |   |   |   |-- novita.md
|   |   |   |   |   |   |-- nvidia.md
|   |   |   |   |   |   |-- nvidia_tensorrt.md
|   |   |   |   |   |   |-- nvidia_triton.md
|   |   |   |   |   |   |-- oci_data_science.md
|   |   |   |   |   |   |-- oci_genai.md
|   |   |   |   |   |   |-- octoai.md
|   |   |   |   |   |   |-- ollama.md
|   |   |   |   |   |   |-- opea.md
|   |   |   |   |   |   |-- openai.md
|   |   |   |   |   |   |-- openai_like.md
|   |   |   |   |   |   |-- openrouter.md
|   |   |   |   |   |   |-- openvino.md
|   |   |   |   |   |   |-- openvino_genai.md
|   |   |   |   |   |   |-- optimum_intel.md
|   |   |   |   |   |   |-- ovhcloud.md
|   |   |   |   |   |   |-- paieas.md
|   |   |   |   |   |   |-- palm.md
|   |   |   |   |   |   |-- perplexity.md
|   |   |   |   |   |   |-- pipeshift.md
|   |   |   |   |   |   |-- portkey.md
|   |   |   |   |   |   |-- predibase.md
|   |   |   |   |   |   |-- premai.md
|   |   |   |   |   |   |-- qianfan.md
|   |   |   |   |   |   |-- reka.md
|   |   |   |   |   |   |-- replicate.md
|   |   |   |   |   |   |-- rungpt.md
|   |   |   |   |   |   |-- sagemaker_endpoint.md
|   |   |   |   |   |   |-- sambanovasystems.md
|   |   |   |   |   |   |-- sarvam.md
|   |   |   |   |   |   |-- servam.md
|   |   |   |   |   |   |-- sglang.md
|   |   |   |   |   |   |-- siliconflow.md
|   |   |   |   |   |   |-- stepfun.md
|   |   |   |   |   |   |-- together.md
|   |   |   |   |   |   |-- upstage.md
|   |   |   |   |   |   |-- vercel_ai_gateway.md
|   |   |   |   |   |   |-- vertex.md
|   |   |   |   |   |   |-- vllm.md
|   |   |   |   |   |   |-- xinference.md
|   |   |   |   |   |   |-- yi.md
|   |   |   |   |   |   |-- you.md
|   |   |   |   |   |   \-- zhipuai.md
|   |   |   |   |   |-- memory
|   |   |   |   |   |   |-- bedrock_agentcore.md
|   |   |   |   |   |   |-- chat_memory_buffer.md
|   |   |   |   |   |   |-- index.md
|   |   |   |   |   |   |-- mem0.md
|   |   |   |   |   |   |-- memory.md
|   |   |   |   |   |   |-- simple_composable_memory.md
|   |   |   |   |   |   \-- vector_memory.md
|   |   |   |   |   |-- node_parser
|   |   |   |   |   |   |-- alibabacloud_aisearch.md
|   |   |   |   |   |   |-- chonkie.md
|   |   |   |   |   |   |-- dashscope.md
|   |   |   |   |   |   |-- docling.md
|   |   |   |   |   |   |-- slide.md
|   |   |   |   |   |   \-- topic.md
|   |   |   |   |   |-- node_parsers
|   |   |   |   |   |   |-- code.md
|   |   |   |   |   |   |-- hierarchical.md
|   |   |   |   |   |   |-- html.md
|   |   |   |   |   |   |-- index.md
|   |   |   |   |   |   |-- json.md
|   |   |   |   |   |   |-- langchain.md
|   |   |   |   |   |   |-- markdown.md
|   |   |   |   |   |   |-- markdown_element.md
|   |   |   |   |   |   |-- semantic_splitter.md
|   |   |   |   |   |   |-- sentence_splitter.md
|   |   |   |   |   |   |-- sentence_window.md
|   |   |   |   |   |   |-- token_text_splitter.md
|   |   |   |   |   |   \-- unstructured_element.md
|   |   |   |   |   |-- objects
|   |   |   |   |   |   \-- index.md
|   |   |   |   |   |-- observability
|   |   |   |   |   |   \-- otel.md
|   |   |   |   |   |-- output_parsers
|   |   |   |   |   |   |-- guardrails.md
|   |   |   |   |   |   |-- index.md
|   |   |   |   |   |   |-- langchain.md
|   |   |   |   |   |   |-- pydantic.md
|   |   |   |   |   |   \-- selection.md
|   |   |   |   |   |-- packs
|   |   |   |   |   |   |-- agent_search_retriever.md
|   |   |   |   |   |   |-- amazon_product_extraction.md
|   |   |   |   |   |   |-- arize_phoenix_query_engine.md
|   |   |   |   |   |   |-- auto_merging_retriever.md
|   |   |   |   |   |   |-- code_hierarchy.md
|   |   |   |   |   |   |-- cohere_citation_chat.md
|   |   |   |   |   |   |-- deeplake_deepmemory_retriever.md
|   |   |   |   |   |   |-- deeplake_multimodal_retrieval.md
|   |   |   |   |   |   |-- dense_x_retrieval.md
|   |   |   |   |   |   |-- diff_private_simple_dataset.md
|   |   |   |   |   |   |-- evaluator_benchmarker.md
|   |   |   |   |   |   |-- fusion_retriever.md
|   |   |   |   |   |   |-- fuzzy_citation.md
|   |   |   |   |   |   |-- gmail_openai_agent.md
|   |   |   |   |   |   |-- index.md
|   |   |   |   |   |   |-- koda_retriever.md
|   |   |   |   |   |   |-- llama_dataset_metadata.md
|   |   |   |   |   |   |-- llama_guard_moderator.md
|   |   |   |   |   |   |-- llava_completion.md
|   |   |   |   |   |   |-- longrag.md
|   |   |   |   |   |   |-- mixture_of_agents.md
|   |   |   |   |   |   |-- multi_tenancy_rag.md
|   |   |   |   |   |   |-- multidoc_autoretrieval.md
|   |   |   |   |   |   |-- nebulagraph_query_engine.md
|   |   |   |   |   |   |-- neo4j_query_engine.md
|   |   |   |   |   |   |-- node_parser_semantic_chunking.md
|   |   |   |   |   |   |-- ollama_query_engine.md
|   |   |   |   |   |   |-- panel_chatbot.md
|   |   |   |   |   |   |-- raft_dataset.md
|   |   |   |   |   |   |-- rag_evaluator.md
|   |   |   |   |   |   |-- ragatouille_retriever.md
|   |   |   |   |   |   |-- raptor.md
|   |   |   |   |   |   |-- recursive_retriever.md
|   |   |   |   |   |   |-- resume_screener.md
|   |   |   |   |   |   |-- retry_engine_weaviate.md
|   |   |   |   |   |   |-- searchain.md
|   |   |   |   |   |   |-- self_discover.md
|   |   |   |   |   |   |-- self_rag.md
|   |   |   |   |   |   |-- sentence_window_retriever.md
|   |   |   |   |   |   |-- snowflake_query_engine.md
|   |   |   |   |   |   |-- stock_market_data_query_engine.md
|   |   |   |   |   |   |-- streamlit_chatbot.md
|   |   |   |   |   |   |-- sub_question_weaviate.md
|   |   |   |   |   |   |-- timescale_vector_autoretrieval.md
|   |   |   |   |   |   |-- trulens_eval_packs.md
|   |   |   |   |   |   |-- vectara_rag.md
|   |   |   |   |   |   |-- voyage_query_engine.md
|   |   |   |   |   |   |-- zenguard.md
|   |   |   |   |   |   \-- zephyr_query_engine.md
|   |   |   |   |   |-- postprocessor
|   |   |   |   |   |   |-- aimon_rerank.md
|   |   |   |   |   |   |-- alibabacloud_aisearch_rerank.md
|   |   |   |   |   |   |-- auto_prev_next.md
|   |   |   |   |   |   |-- bedrock_rerank.md
|   |   |   |   |   |   |-- cohere_rerank.md
|   |   |   |   |   |   |-- colbert_rerank.md
|   |   |   |   |   |   |-- colpali_rerank.md
|   |   |   |   |   |   |-- contextual_rerank.md
|   |   |   |   |   |   |-- dashscope_rerank.md
|   |   |   |   |   |   |-- embedding_recency.md
|   |   |   |   |   |   |-- fixed_recency.md
|   |   |   |   |   |   |-- flag_embedding_reranker.md
|   |   |   |   |   |   |-- flashrank_rerank.md
|   |   |   |   |   |   |-- ibm.md
|   |   |   |   |   |   |-- index.md
|   |   |   |   |   |   |-- jinaai_rerank.md
|   |   |   |   |   |   |-- keyword.md
|   |   |   |   |   |   |-- llm_rerank.md
|   |   |   |   |   |   |-- long_context_reorder.md
|   |   |   |   |   |   |-- longllmlingua.md
|   |   |   |   |   |   |-- metadata_replacement.md
|   |   |   |   |   |   |-- mixedbreadai_rerank.md
|   |   |   |   |   |   |-- NER_PII.md
|   |   |   |   |   |   |-- nvidia_rerank.md
|   |   |   |   |   |   |-- openvino_rerank.md
|   |   |   |   |   |   |-- PII.md
|   |   |   |   |   |   |-- pinecone_native_rerank.md
|   |   |   |   |   |   |-- presidio.md
|   |   |   |   |   |   |-- prev_next.md
|   |   |   |   |   |   |-- rankgpt_rerank.md
|   |   |   |   |   |   |-- rankllm_rerank.md
|   |   |   |   |   |   |-- sbert_rerank.md
|   |   |   |   |   |   |-- sentence_optimizer.md
|   |   |   |   |   |   |-- siliconflow_rerank.md
|   |   |   |   |   |   |-- similarity.md
|   |   |   |   |   |   |-- tei_rerank.md
|   |   |   |   |   |   |-- time_weighted.md
|   |   |   |   |   |   |-- voyageai_rerank.md
|   |   |   |   |   |   \-- xinference_rerank.md
|   |   |   |   |   |-- program
|   |   |   |   |   |   |-- evaporate.md
|   |   |   |   |   |   |-- guidance.md
|   |   |   |   |   |   |-- index.md
|   |   |   |   |   |   |-- llm_text_completion.md
|   |   |   |   |   |   |-- lmformatenforcer.md
|   |   |   |   |   |   \-- multi_modal.md
|   |   |   |   |   |-- prompts
|   |   |   |   |   |   \-- index.md
|   |   |   |   |   |-- protocols
|   |   |   |   |   |   \-- ag_ui.md
|   |   |   |   |   |-- query_engine
|   |   |   |   |   |   |-- citation.md
|   |   |   |   |   |   |-- cogniswitch.md
|   |   |   |   |   |   |-- custom.md
|   |   |   |   |   |   |-- FLARE.md
|   |   |   |   |   |   |-- index.md
|   |   |   |   |   |   |-- JSONalayze.md
|   |   |   |   |   |   |-- knowledge_graph.md
|   |   |   |   |   |   |-- multi_step.md
|   |   |   |   |   |   |-- NL_SQL_table.md
|   |   |   |   |   |   |-- pandas.md
|   |   |   |   |   |   |-- PGVector_SQL.md
|   |   |   |   |   |   |-- polars.md
|   |   |   |   |   |   |-- retriever.md
|   |   |   |   |   |   |-- retriever_router.md
|   |   |   |   |   |   |-- retry.md
|   |   |   |   |   |   |-- router.md
|   |   |   |   |   |   |-- simple_multi_modal.md
|   |   |   |   |   |   |-- SQL_join.md
|   |   |   |   |   |   |-- SQL_table_retriever.md
|   |   |   |   |   |   |-- sub_question.md
|   |   |   |   |   |   |-- tool_retriever_router.md
|   |   |   |   |   |   \-- transform.md
|   |   |   |   |   |-- question_gen
|   |   |   |   |   |   |-- guidance.md
|   |   |   |   |   |   |-- index.md
|   |   |   |   |   |   \-- llm_question_gen.md
|   |   |   |   |   |-- readers
|   |   |   |   |   |   |-- agent_search.md
|   |   |   |   |   |   |-- airbyte_cdk.md
|   |   |   |   |   |   |-- airbyte_gong.md
|   |   |   |   |   |   |-- airbyte_hubspot.md
|   |   |   |   |   |   |-- airbyte_salesforce.md
|   |   |   |   |   |   |-- airbyte_shopify.md
|   |   |   |   |   |   |-- airbyte_stripe.md
|   |   |   |   |   |   |-- airbyte_typeform.md
|   |   |   |   |   |   |-- airbyte_zendesk_support.md
|   |   |   |   |   |   |-- airtable.md
|   |   |   |   |   |   |-- alibabacloud_aisearch.md
|   |   |   |   |   |   |-- apify.md
|   |   |   |   |   |   |-- arango_db.md
|   |   |   |   |   |   |-- arxiv.md
|   |   |   |   |   |   |-- asana.md
|   |   |   |   |   |   |-- assemblyai.md
|   |   |   |   |   |   |-- astra_db.md
|   |   |   |   |   |   |-- athena.md
|   |   |   |   |   |   |-- awadb.md
|   |   |   |   |   |   |-- azcognitive_search.md
|   |   |   |   |   |   |-- azstorage_blob.md
|   |   |   |   |   |   |-- bagel.md
|   |   |   |   |   |   |-- bilibili.md
|   |   |   |   |   |   |-- bitbucket.md
|   |   |   |   |   |   |-- boarddocs.md
|   |   |   |   |   |   |-- box.md
|   |   |   |   |   |   |-- chatgpt_plugin.md
|   |   |   |   |   |   |-- chroma.md
|   |   |   |   |   |   |-- confluence.md
|   |   |   |   |   |   |-- couchbase.md
|   |   |   |   |   |   |-- couchdb.md
|   |   |   |   |   |   |-- dad_jokes.md
|   |   |   |   |   |   |-- dashscope.md
|   |   |   |   |   |   |-- dashvector.md
|   |   |   |   |   |   |-- database.md
|   |   |   |   |   |   |-- datasets.md
|   |   |   |   |   |   |-- deeplake.md
|   |   |   |   |   |   |-- discord.md
|   |   |   |   |   |   |-- docling.md
|   |   |   |   |   |   |-- docstring_walker.md
|   |   |   |   |   |   |-- docugami.md
|   |   |   |   |   |   |-- document360.md
|   |   |   |   |   |   |-- earnings_call_transcript.md
|   |   |   |   |   |   |-- elasticsearch.md
|   |   |   |   |   |   |-- faiss.md
|   |   |   |   |   |   |-- feedly_rss.md
|   |   |   |   |   |   |-- feishu_docs.md
|   |   |   |   |   |   |-- file.md
|   |   |   |   |   |   |-- firebase_realtimedb.md
|   |   |   |   |   |   |-- firestore.md
|   |   |   |   |   |   |-- gcs.md
|   |   |   |   |   |   |-- genius.md
|   |   |   |   |   |   |-- gitbook.md
|   |   |   |   |   |   |-- github.md
|   |   |   |   |   |   |-- gitlab.md
|   |   |   |   |   |   |-- google.md
|   |   |   |   |   |   |-- gpt_repo.md
|   |   |   |   |   |   |-- graphdb_cypher.md
|   |   |   |   |   |   |-- graphql.md
|   |   |   |   |   |   |-- guru.md
|   |   |   |   |   |   |-- hatena_blog.md
|   |   |   |   |   |   |-- hubspot.md
|   |   |   |   |   |   |-- huggingface_fs.md
|   |   |   |   |   |   |-- hwp.md
|   |   |   |   |   |   |-- iceberg.md
|   |   |   |   |   |   |-- imdb_review.md
|   |   |   |   |   |   |-- index.md
|   |   |   |   |   |   |-- intercom.md
|   |   |   |   |   |   |-- jaguar.md
|   |   |   |   |   |   |-- jira.md
|   |   |   |   |   |   |-- joplin.md
|   |   |   |   |   |   |-- json.md
|   |   |   |   |   |   |-- kaltura_esearch.md
|   |   |   |   |   |   |-- kibela.md
|   |   |   |   |   |   |-- layoutir.md
|   |   |   |   |   |   |-- legacy_office.md
|   |   |   |   |   |   |-- lilac.md
|   |   |   |   |   |   |-- linear.md
|   |   |   |   |   |   |-- llama_parse.md
|   |   |   |   |   |   |-- macrometa_gdn.md
|   |   |   |   |   |   |-- make_com.md
|   |   |   |   |   |   |-- mangadex.md
|   |   |   |   |   |   |-- mangoapps_guides.md
|   |   |   |   |   |   |-- maps.md
|   |   |   |   |   |   |-- markitdown.md
|   |   |   |   |   |   |-- mbox.md
|   |   |   |   |   |   |-- memos.md
|   |   |   |   |   |   |-- metal.md
|   |   |   |   |   |   |-- microsoft_onedrive.md
|   |   |   |   |   |   |-- microsoft_outlook.md
|   |   |   |   |   |   |-- microsoft_outlook_emails.md
|   |   |   |   |   |   |-- microsoft_sharepoint.md
|   |   |   |   |   |   |-- milvus.md
|   |   |   |   |   |   |-- minio.md
|   |   |   |   |   |   |-- mondaydotcom.md
|   |   |   |   |   |   |-- mongodb.md
|   |   |   |   |   |   |-- myscale.md
|   |   |   |   |   |   |-- notion.md
|   |   |   |   |   |   |-- nougat_ocr.md
|   |   |   |   |   |   |-- obsidian.md
|   |   |   |   |   |   |-- openalex.md
|   |   |   |   |   |   |-- opendal.md
|   |   |   |   |   |   |-- opensearch.md
|   |   |   |   |   |   |-- oracleai.md
|   |   |   |   |   |   |-- oxylabs.md
|   |   |   |   |   |   |-- paddle_ocr.md
|   |   |   |   |   |   |-- pandas_ai.md
|   |   |   |   |   |   |-- papers.md
|   |   |   |   |   |   |-- patentsview.md
|   |   |   |   |   |   |-- pathway.md
|   |   |   |   |   |   |-- pdb.md
|   |   |   |   |   |   |-- pdf_marker.md
|   |   |   |   |   |   |-- pdf_table.md
|   |   |   |   |   |   |-- pebblo.md
|   |   |   |   |   |   |-- preprocess.md
|   |   |   |   |   |   |-- psychic.md
|   |   |   |   |   |   |-- qdrant.md
|   |   |   |   |   |   |-- quip.md
|   |   |   |   |   |   |-- rayyan.md
|   |   |   |   |   |   |-- readwise.md
|   |   |   |   |   |   |-- reddit.md
|   |   |   |   |   |   |-- remote.md
|   |   |   |   |   |   |-- remote_depth.md
|   |   |   |   |   |   |-- s3.md
|   |   |   |   |   |   |-- sec_filings.md
|   |   |   |   |   |   |-- semanticscholar.md
|   |   |   |   |   |   |-- service_now.md
|   |   |   |   |   |   |-- simple_directory_reader.md
|   |   |   |   |   |   |-- singlestore.md
|   |   |   |   |   |   |-- slack.md
|   |   |   |   |   |   |-- smart_pdf_loader.md
|   |   |   |   |   |   |-- snowflake.md
|   |   |   |   |   |   |-- solr.md
|   |   |   |   |   |   |-- spotify.md
|   |   |   |   |   |   |-- stackoverflow.md
|   |   |   |   |   |   |-- steamship.md
|   |   |   |   |   |   |-- string_iterable.md
|   |   |   |   |   |   |-- stripe_docs.md
|   |   |   |   |   |   |-- structured_data.md
|   |   |   |   |   |   |-- telegram.md
|   |   |   |   |   |   |-- toggl.md
|   |   |   |   |   |   |-- trello.md
|   |   |   |   |   |   |-- twitter.md
|   |   |   |   |   |   |-- txtai.md
|   |   |   |   |   |   |-- uniprot.md
|   |   |   |   |   |   |-- upstage.md
|   |   |   |   |   |   |-- weather.md
|   |   |   |   |   |   |-- weaviate.md
|   |   |   |   |   |   |-- web.md
|   |   |   |   |   |   |-- whatsapp.md
|   |   |   |   |   |   |-- whisper.md
|   |   |   |   |   |   |-- wikipedia.md
|   |   |   |   |   |   |-- wordlift.md
|   |   |   |   |   |   |-- wordpress.md
|   |   |   |   |   |   |-- youtube_transcript.md
|   |   |   |   |   |   |-- zendesk.md
|   |   |   |   |   |   |-- zep.md
|   |   |   |   |   |   |-- zulip.md
|   |   |   |   |   |   \-- zyte_serp.md
|   |   |   |   |   |-- response_synthesizers
|   |   |   |   |   |   |-- accumulate.md
|   |   |   |   |   |   |-- compact_accumulate.md
|   |   |   |   |   |   |-- compact_and_refine.md
|   |   |   |   |   |   |-- generation.md
|   |   |   |   |   |   |-- google.md
|   |   |   |   |   |   |-- index.md
|   |   |   |   |   |   |-- refine.md
|   |   |   |   |   |   |-- simple_summarize.md
|   |   |   |   |   |   \-- tree_summarize.md
|   |   |   |   |   |-- retrievers
|   |   |   |   |   |   |-- alletra_x10000_retriever.md
|   |   |   |   |   |   |-- auto_merging.md
|   |   |   |   |   |   |-- bedrock.md
|   |   |   |   |   |   |-- bm25.md
|   |   |   |   |   |   |-- duckdb_retriever.md
|   |   |   |   |   |   |-- galaxia.md
|   |   |   |   |   |   |-- index.md
|   |   |   |   |   |   |-- kendra.md
|   |   |   |   |   |   |-- keyword.md
|   |   |   |   |   |   |-- knowledge_graph.md
|   |   |   |   |   |   |-- mongodb_atlas_bm25_retriever.md
|   |   |   |   |   |   |-- pathway.md
|   |   |   |   |   |   |-- query_fusion.md
|   |   |   |   |   |   |-- recursive.md
|   |   |   |   |   |   |-- router.md
|   |   |   |   |   |   |-- sql.md
|   |   |   |   |   |   |-- summary.md
|   |   |   |   |   |   |-- superlinked.md
|   |   |   |   |   |   |-- tldw.md
|   |   |   |   |   |   |-- transform.md
|   |   |   |   |   |   |-- tree.md
|   |   |   |   |   |   |-- vector.md
|   |   |   |   |   |   |-- vectorize.md
|   |   |   |   |   |   |-- vertexai_search.md
|   |   |   |   |   |   |-- videodb.md
|   |   |   |   |   |   \-- you.md
|   |   |   |   |   |-- schema
|   |   |   |   |   |   \-- index.md
|   |   |   |   |   |-- selectors
|   |   |   |   |   |   \-- notdiamond.md
|   |   |   |   |   |-- sparse_embeddings
|   |   |   |   |   |   \-- fastembed.md
|   |   |   |   |   |-- storage
|   |   |   |   |   |   |-- chat_store
|   |   |   |   |   |   |   |-- async_sql.md
|   |   |   |   |   |   |   |-- azure.md
|   |   |   |   |   |   |   |-- azurecosmosmongovcore.md
|   |   |   |   |   |   |   |-- azurecosmosnosql.md
|   |   |   |   |   |   |   |-- dynamodb.md
|   |   |   |   |   |   |   |-- gel.md
|   |   |   |   |   |   |   |-- index.md
|   |   |   |   |   |   |   |-- mongo.md
|   |   |   |   |   |   |   |-- postgres.md
|   |   |   |   |   |   |   |-- redis.md
|   |   |   |   |   |   |   |-- simple.md
|   |   |   |   |   |   |   |-- sqlite.md
|   |   |   |   |   |   |   |-- tablestore.md
|   |   |   |   |   |   |   |-- upstash.md
|   |   |   |   |   |   |   \-- yugabytedb.md
|   |   |   |   |   |   |-- docstore
|   |   |   |   |   |   |   |-- azure.md
|   |   |   |   |   |   |   |-- azurecosmosnosql.md
|   |   |   |   |   |   |   |-- couchbase.md
|   |   |   |   |   |   |   |-- duckdb.md
|   |   |   |   |   |   |   |-- dynamodb.md
|   |   |   |   |   |   |   |-- elasticsearch.md
|   |   |   |   |   |   |   |-- firestore.md
|   |   |   |   |   |   |   |-- gel.md
|   |   |   |   |   |   |   |-- index.md
|   |   |   |   |   |   |   |-- mongodb.md
|   |   |   |   |   |   |   |-- postgres.md
|   |   |   |   |   |   |   |-- redis.md
|   |   |   |   |   |   |   |-- simple.md
|   |   |   |   |   |   |   \-- tablestore.md
|   |   |   |   |   |   |-- graph_stores
|   |   |   |   |   |   |   |-- ApertureDB.md
|   |   |   |   |   |   |   |-- falkordb.md
|   |   |   |   |   |   |   |-- index.md
|   |   |   |   |   |   |   |-- memgraph.md
|   |   |   |   |   |   |   |-- nebula.md
|   |   |   |   |   |   |   |-- neo4j.md
|   |   |   |   |   |   |   |-- neptune.md
|   |   |   |   |   |   |   |-- simple.md
|   |   |   |   |   |   |   \-- tidb.md
|   |   |   |   |   |   |-- index_store
|   |   |   |   |   |   |   |-- azure.md
|   |   |   |   |   |   |   |-- azurecosmosnosql.md
|   |   |   |   |   |   |   |-- couchbase.md
|   |   |   |   |   |   |   |-- duckdb.md
|   |   |   |   |   |   |   |-- dynamodb.md
|   |   |   |   |   |   |   |-- elasticsearch.md
|   |   |   |   |   |   |   |-- firestore.md
|   |   |   |   |   |   |   |-- gel.md
|   |   |   |   |   |   |   |-- index.md
|   |   |   |   |   |   |   |-- mongodb.md
|   |   |   |   |   |   |   |-- postgres.md
|   |   |   |   |   |   |   |-- redis.md
|   |   |   |   |   |   |   |-- simple.md
|   |   |   |   |   |   |   \-- tablestore.md
|   |   |   |   |   |   |-- kvstore
|   |   |   |   |   |   |   |-- azure.md
|   |   |   |   |   |   |   |-- azurecosmosnosql.md
|   |   |   |   |   |   |   |-- couchbase.md
|   |   |   |   |   |   |   |-- duckdb.md
|   |   |   |   |   |   |   |-- dynamodb.md
|   |   |   |   |   |   |   |-- elasticsearch.md
|   |   |   |   |   |   |   |-- firestore.md
|   |   |   |   |   |   |   |-- gel.md
|   |   |   |   |   |   |   |-- index.md
|   |   |   |   |   |   |   |-- mongodb.md
|   |   |   |   |   |   |   |-- postgres.md
|   |   |   |   |   |   |   |-- redis.md
|   |   |   |   |   |   |   |-- s3.md
|   |   |   |   |   |   |   |-- simple.md
|   |   |   |   |   |   |   \-- tablestore.md
|   |   |   |   |   |   |-- vector_store
|   |   |   |   |   |   |   |-- alibabacloud_mysql.md
|   |   |   |   |   |   |   |-- alibabacloud_opensearch.md
|   |   |   |   |   |   |   |-- analyticdb.md
|   |   |   |   |   |   |   |-- ApertureDB.md
|   |   |   |   |   |   |   |-- astra_db.md
|   |   |   |   |   |   |   |-- awadb.md
|   |   |   |   |   |   |   |-- awsdocdb.md
|   |   |   |   |   |   |   |-- azure_postgres.md
|   |   |   |   |   |   |   |-- azureaisearch.md
|   |   |   |   |   |   |   |-- azurecosmosmongo.md
|   |   |   |   |   |   |   |-- azurecosmosnosql.md
|   |   |   |   |   |   |   |-- bagel.md
|   |   |   |   |   |   |   |-- baiduvectordb.md
|   |   |   |   |   |   |   |-- bigquery.md
|   |   |   |   |   |   |   |-- cassandra.md
|   |   |   |   |   |   |   |-- chroma.md
|   |   |   |   |   |   |   |-- clickhouse.md
|   |   |   |   |   |   |   |-- couchbase.md
|   |   |   |   |   |   |   |-- dashvector.md
|   |   |   |   |   |   |   |-- databricks.md
|   |   |   |   |   |   |   |-- db2.md
|   |   |   |   |   |   |   |-- deeplake.md
|   |   |   |   |   |   |   |-- docarray.md
|   |   |   |   |   |   |   |-- duckdb.md
|   |   |   |   |   |   |   |-- dynamodb.md
|   |   |   |   |   |   |   |-- elasticsearch.md
|   |   |   |   |   |   |   |-- epsilla.md
|   |   |   |   |   |   |   |-- faiss.md
|   |   |   |   |   |   |   |-- firestore.md
|   |   |   |   |   |   |   |-- gel.md
|   |   |   |   |   |   |   |-- google.md
|   |   |   |   |   |   |   |-- hologres.md
|   |   |   |   |   |   |   |-- index.md
|   |   |   |   |   |   |   |-- jaguar.md
|   |   |   |   |   |   |   |-- kdbai.md
|   |   |   |   |   |   |   |-- lancedb.md
|   |   |   |   |   |   |   |-- lantern.md
|   |   |   |   |   |   |   |-- lindorm.md
|   |   |   |   |   |   |   |-- mariadb.md
|   |   |   |   |   |   |   |-- milvus.md
|   |   |   |   |   |   |   |-- mongodb.md
|   |   |   |   |   |   |   |-- moorcheh.md
|   |   |   |   |   |   |   |-- neo4jvector.md
|   |   |   |   |   |   |   |-- neptune.md
|   |   |   |   |   |   |   |-- nile.md
|   |   |   |   |   |   |   |-- objectbox.md
|   |   |   |   |   |   |   |-- oceanbase.md
|   |   |   |   |   |   |   |-- openGauss.md
|   |   |   |   |   |   |   |-- opensearch.md
|   |   |   |   |   |   |   |-- oracledb.md
|   |   |   |   |   |   |   |-- pgvecto_rs.md
|   |   |   |   |   |   |   |-- pinecone.md
|   |   |   |   |   |   |   |-- postgres.md
|   |   |   |   |   |   |   |-- qdrant.md
|   |   |   |   |   |   |   |-- redis.md
|   |   |   |   |   |   |   |-- relyt.md
|   |   |   |   |   |   |   |-- rocksetdb.md
|   |   |   |   |   |   |   |-- s3.md
|   |   |   |   |   |   |   |-- simple.md
|   |   |   |   |   |   |   |-- singlestoredb.md
|   |   |   |   |   |   |   |-- solr.md
|   |   |   |   |   |   |   |-- supabase.md
|   |   |   |   |   |   |   |-- tablestore.md
|   |   |   |   |   |   |   |-- tair.md
|   |   |   |   |   |   |   |-- tencentvectordb.md
|   |   |   |   |   |   |   |-- tidbvector.md
|   |   |   |   |   |   |   |-- timescalevector.md
|   |   |   |   |   |   |   |-- txtai.md
|   |   |   |   |   |   |   |-- typesense.md
|   |   |   |   |   |   |   |-- upstash.md
|   |   |   |   |   |   |   |-- vearch.md
|   |   |   |   |   |   |   |-- vectorx.md
|   |   |   |   |   |   |   |-- vertexaivectorsearch.md
|   |   |   |   |   |   |   |-- vespa.md
|   |   |   |   |   |   |   |-- volcengine_mysql.md
|   |   |   |   |   |   |   |-- weaviate.md
|   |   |   |   |   |   |   |-- wordlift.md
|   |   |   |   |   |   |   |-- yugabytedb.md
|   |   |   |   |   |   |   \-- zep.md
|   |   |   |   |   |   \-- storage_context.md
|   |   |   |   |   |-- tools
|   |   |   |   |   |   |-- agentql.md
|   |   |   |   |   |   |-- airweave.md
|   |   |   |   |   |   |-- artifact_editor.md
|   |   |   |   |   |   |-- arxiv.md
|   |   |   |   |   |   |-- aws_bedrock_agentcore.md
|   |   |   |   |   |   |-- azure_code_interpreter.md
|   |   |   |   |   |   |-- azure_cv.md
|   |   |   |   |   |   |-- azure_speech.md
|   |   |   |   |   |   |-- azure_translate.md
|   |   |   |   |   |   |-- bing_search.md
|   |   |   |   |   |   |-- box.md
|   |   |   |   |   |   |-- brave_search.md
|   |   |   |   |   |   |-- brightdata.md
|   |   |   |   |   |   |-- cassandra.md
|   |   |   |   |   |   |-- chatgpt_plugin.md
|   |   |   |   |   |   |-- code_interpreter.md
|   |   |   |   |   |   |-- cogniswitch.md
|   |   |   |   |   |   |-- dappier.md
|   |   |   |   |   |   |-- database.md
|   |   |   |   |   |   |-- desearch.md
|   |   |   |   |   |   |-- duckduckgo.md
|   |   |   |   |   |   |-- elevenlabs.md
|   |   |   |   |   |   |-- exa.md
|   |   |   |   |   |   |-- finance.md
|   |   |   |   |   |   |-- function.md
|   |   |   |   |   |   |-- google.md
|   |   |   |   |   |   |-- graphql.md
|   |   |   |   |   |   |-- hive.md
|   |   |   |   |   |   |-- index.md
|   |   |   |   |   |   |-- ionic_shopping.md
|   |   |   |   |   |   |-- jina.md
|   |   |   |   |   |   |-- jira.md
|   |   |   |   |   |   |-- jira_issue.md
|   |   |   |   |   |   |-- linkup_research.md
|   |   |   |   |   |   |-- load_and_search.md
|   |   |   |   |   |   |-- mcp.md
|   |   |   |   |   |   |-- mcp_discovery.md
|   |   |   |   |   |   |-- measurespace.md
|   |   |   |   |   |   |-- metaphor.md
|   |   |   |   |   |   |-- moss.md
|   |   |   |   |   |   |-- multion.md
|   |   |   |   |   |   |-- neo4j.md
|   |   |   |   |   |   |-- notion.md
|   |   |   |   |   |   |-- ondemand_loader.md
|   |   |   |   |   |   |-- openai.md
|   |   |   |   |   |   |-- openapi.md
|   |   |   |   |   |   |-- parallel_web_systems.md
|   |   |   |   |   |   |-- playgrounds.md
|   |   |   |   |   |   |-- playwright.md
|   |   |   |   |   |   |-- python_file.md
|   |   |   |   |   |   |-- query_engine.md
|   |   |   |   |   |   |-- requests.md
|   |   |   |   |   |   |-- retriever.md
|   |   |   |   |   |   |-- salesforce.md
|   |   |   |   |   |   |-- scrapegraph.md
|   |   |   |   |   |   |-- seltz.md
|   |   |   |   |   |   |-- serpex.md
|   |   |   |   |   |   |-- shopify.md
|   |   |   |   |   |   |-- signnow.md
|   |   |   |   |   |   |-- slack.md
|   |   |   |   |   |   |-- tavily_research.md
|   |   |   |   |   |   |-- text_to_image.md
|   |   |   |   |   |   |-- tool_spec.md
|   |   |   |   |   |   |-- typecast.md
|   |   |   |   |   |   |-- valyu.md
|   |   |   |   |   |   |-- vectara_query.md
|   |   |   |   |   |   |-- vector_db.md
|   |   |   |   |   |   |-- waii.md
|   |   |   |   |   |   |-- weather.md
|   |   |   |   |   |   |-- wikipedia.md
|   |   |   |   |   |   |-- wolfram_alpha.md
|   |   |   |   |   |   |-- yahoo_finance.md
|   |   |   |   |   |   |-- yelp.md
|   |   |   |   |   |   \-- zapier.md
|   |   |   |   |   |-- voice_agents
|   |   |   |   |   |   |-- elevenlabs.md
|   |   |   |   |   |   |-- gemini_live.md
|   |   |   |   |   |   \-- openai.md
|   |   |   |   |   |-- workflow
|   |   |   |   |   |   \-- .gitkeep
|   |   |   |   |   \-- index.md
|   |   |   |   |-- overrides
|   |   |   |   |   |-- partials
|   |   |   |   |   |   \-- copyright.html
|   |   |   |   |   \-- main.html
|   |   |   |   |-- mkdocs.yml
|   |   |   |   |-- poetry.lock
|   |   |   |   \-- pyproject.toml
|   |   |   |-- examples
|   |   |   |   |-- agent
|   |   |   |   |   |-- memory
|   |   |   |   |   |   |-- chat_memory_buffer.ipynb
|   |   |   |   |   |   |-- composable_memory.ipynb
|   |   |   |   |   |   |-- summary_memory_buffer.ipynb
|   |   |   |   |   |   \-- vector_memory.ipynb
|   |   |   |   |   |-- agent_builder.ipynb
|   |   |   |   |   |-- agent_with_structured_output.ipynb
|   |   |   |   |   |-- agent_workflow_basic.ipynb
|   |   |   |   |   |-- agent_workflow_multi.ipynb
|   |   |   |   |   |-- agent_workflow_research_assistant.ipynb
|   |   |   |   |   |-- agents_as_tools.ipynb
|   |   |   |   |   |-- anthropic_agent.ipynb
|   |   |   |   |   |-- bedrock_converse_agent.ipynb
|   |   |   |   |   |-- Chatbot_SEC.ipynb
|   |   |   |   |   |-- code_act_agent.ipynb
|   |   |   |   |   |-- custom_multi_agent.ipynb
|   |   |   |   |   |-- from_scratch_code_act_agent.ipynb
|   |   |   |   |   |-- gemini_agent.ipynb
|   |   |   |   |   |-- mistral_agent.ipynb
|   |   |   |   |   |-- multi_agent_workflow_with_weaviate_queryagent.ipynb
|   |   |   |   |   |-- multi_document_agents-v1.ipynb
|   |   |   |   |   |-- nvidia_agent.ipynb
|   |   |   |   |   |-- nvidia_document_research_assistant_for_blog_creation.ipynb
|   |   |   |   |   |-- nvidia_sub_question_query_engine.ipynb
|   |   |   |   |   |-- openai_agent_context_retrieval.ipynb
|   |   |   |   |   |-- openai_agent_lengthy_tools.ipynb
|   |   |   |   |   |-- openai_agent_query_cookbook.ipynb
|   |   |   |   |   |-- openai_agent_retrieval.ipynb
|   |   |   |   |   |-- openai_agent_with_query_engine.ipynb
|   |   |   |   |   |-- react_agent.ipynb
|   |   |   |   |   |-- react_agent_with_query_engine.ipynb
|   |   |   |   |   \-- return_direct_agent.ipynb
|   |   |   |   |-- benchmarks
|   |   |   |   |   |-- gemini_tool_selection_eval.ipynb
|   |   |   |   |   \-- phi-3-mini-4k-instruct.ipynb
|   |   |   |   |-- chat_engine
|   |   |   |   |   |-- chat_engine_best.ipynb
|   |   |   |   |   |-- chat_engine_condense_plus_context.ipynb
|   |   |   |   |   |-- chat_engine_condense_question.ipynb
|   |   |   |   |   |-- chat_engine_context.ipynb
|   |   |   |   |   |-- chat_engine_personality.ipynb
|   |   |   |   |   \-- chat_engine_repl.ipynb
|   |   |   |   |-- chat_store
|   |   |   |   |   |-- AlloyDBChatStoreDemo.ipynb
|   |   |   |   |   |-- AzureChatStoreDemo.ipynb
|   |   |   |   |   \-- CloudSQLPgChatStoreDemo.ipynb
|   |   |   |   |-- citation
|   |   |   |   |   \-- pdf_page_reference.ipynb
|   |   |   |   |-- cookbooks
|   |   |   |   |   |-- oreilly_course_cookbooks
|   |   |   |   |   |   |-- Module-2
|   |   |   |   |   |   |   \-- Components_Of_LlamaIndex.ipynb
|   |   |   |   |   |   |-- Module-3
|   |   |   |   |   |   |   \-- Evaluating_RAG_Systems.ipynb
|   |   |   |   |   |   |-- Module-4
|   |   |   |   |   |   |   |-- Ingestion_Pipeline.ipynb
|   |   |   |   |   |   |   \-- Metadata_Extraction.ipynb
|   |   |   |   |   |   |-- Module-5
|   |   |   |   |   |   |   \-- Observability.ipynb
|   |   |   |   |   |   |-- Module-6
|   |   |   |   |   |   |   |-- Agents.ipynb
|   |   |   |   |   |   |   \-- Router_And_SubQuestion_QueryEngine.ipynb
|   |   |   |   |   |   |-- Module-7
|   |   |   |   |   |   |   \-- Multi_Modal_RAG_System.ipynb
|   |   |   |   |   |   |-- Module-8
|   |   |   |   |   |   |   \-- Advanced_RAG_with_LlamaParse.ipynb
|   |   |   |   |   |   \-- README.md
|   |   |   |   |   |-- airtrain.ipynb
|   |   |   |   |   |-- anthropic_haiku.ipynb
|   |   |   |   |   |-- build_knowledge_graph_with_neo4j_llamacloud.ipynb
|   |   |   |   |   |-- cleanlab_tlm_rag.ipynb
|   |   |   |   |   |-- codestral.ipynb
|   |   |   |   |   |-- cohere_retriever_eval.ipynb
|   |   |   |   |   |-- contextual_retrieval.ipynb
|   |   |   |   |   |-- crewai_llamaindex.ipynb
|   |   |   |   |   |-- GraphRAG_v1.ipynb
|   |   |   |   |   |-- GraphRAG_v2.ipynb
|   |   |   |   |   |-- llama3_cookbook.ipynb
|   |   |   |   |   |-- llama3_cookbook_gaudi.ipynb
|   |   |   |   |   |-- llama3_cookbook_groq.ipynb
|   |   |   |   |   |-- llama3_cookbook_ollama_replicate.ipynb
|   |   |   |   |   |-- local_rag_with_chroma_and_ollama.ipynb
|   |   |   |   |   |-- mistralai.ipynb
|   |   |   |   |   |-- mixedbread_reranker.ipynb
|   |   |   |   |   |-- mongodb_retrieval_strategies.ipynb
|   |   |   |   |   |-- ollama_gpt_oss_cookbook.ipynb
|   |   |   |   |   |-- oracleai_demo.ipynb
|   |   |   |   |   |-- prometheus2_cookbook.ipynb
|   |   |   |   |   |-- rerank_llamaparsed_pdfs.ipynb
|   |   |   |   |   \-- toolhouse_llamaindex.ipynb
|   |   |   |   |-- customization
|   |   |   |   |   |-- llms
|   |   |   |   |   |   |-- AzureOpenAI.ipynb
|   |   |   |   |   |   |-- SimpleIndexDemo-ChatGPT.ipynb
|   |   |   |   |   |   |-- SimpleIndexDemo-Huggingface_camel.ipynb
|   |   |   |   |   |   \-- SimpleIndexDemo-Huggingface_stablelm.ipynb
|   |   |   |   |   |-- prompts
|   |   |   |   |   |   |-- chat_prompts.ipynb
|   |   |   |   |   |   \-- completion_prompts.ipynb
|   |   |   |   |   \-- streaming
|   |   |   |   |       |-- chat_engine_condense_question_stream_response.ipynb
|   |   |   |   |       \-- SimpleIndexDemo-streaming.ipynb
|   |   |   |   |-- data
|   |   |   |   |   |-- 10k
|   |   |   |   |   |   |-- lyft_2021.pdf
|   |   |   |   |   |   \-- uber_2021.pdf
|   |   |   |   |   |-- 10q
|   |   |   |   |   |   |-- uber_10q_june_2022.pdf
|   |   |   |   |   |   |-- uber_10q_march_2022.pdf
|   |   |   |   |   |   \-- uber_10q_sept_2022.pdf
|   |   |   |   |   |-- csv
|   |   |   |   |   |   |-- commit_history.csv
|   |   |   |   |   |   |-- commit_history_2.csv
|   |   |   |   |   |   \-- titanic_train.csv
|   |   |   |   |   |-- email
|   |   |   |   |   |   |-- ark-trading-jan-12-2024.eml
|   |   |   |   |   |   \-- ark-trading-jan-12-2024.msg
|   |   |   |   |   |-- figures
|   |   |   |   |   |   \-- image_figure_slides.pdf
|   |   |   |   |   |-- gpt4_experiments
|   |   |   |   |   |   |-- llama2_mistral.png
|   |   |   |   |   |   |-- llama2_model_analysis.png
|   |   |   |   |   |   \-- llama2_violations_charts.png
|   |   |   |   |   |-- images
|   |   |   |   |   |   |-- ark_email_sample.PNG
|   |   |   |   |   |   \-- prometheus_paper_card.png
|   |   |   |   |   \-- paul_graham
|   |   |   |   |       |-- paul_graham_essay.txt
|   |   |   |   |       \-- paul_graham_essay_ambiguated.txt
|   |   |   |   |-- data_connectors
|   |   |   |   |   |-- deplot
|   |   |   |   |   |   |-- biden_popularity.png
|   |   |   |   |   |   |-- DeplotReader.ipynb
|   |   |   |   |   |   |-- marine_chart.png
|   |   |   |   |   |   \-- pew1.png
|   |   |   |   |   |-- AlloyDBReaderDemo.ipynb
|   |   |   |   |   |-- ChromaDemo.ipynb
|   |   |   |   |   |-- CloudSQLPgReaderDemo.ipynb
|   |   |   |   |   |-- DashvectorReaderDemo.ipynb
|   |   |   |   |   |-- DatabaseReaderDemo.ipynb
|   |   |   |   |   |-- DeepLakeReader.ipynb
|   |   |   |   |   |-- DiscordDemo.ipynb
|   |   |   |   |   |-- DoclingReaderDemo.ipynb
|   |   |   |   |   |-- FaissDemo.ipynb
|   |   |   |   |   |-- GithubRepositoryReaderDemo.ipynb
|   |   |   |   |   |-- GoogleChatDemo.ipynb
|   |   |   |   |   |-- GoogleDocsDemo.ipynb
|   |   |   |   |   |-- GoogleDriveDemo.ipynb
|   |   |   |   |   |-- GoogleMapsTextSearchReaderDemo.ipynb
|   |   |   |   |   |-- GoogleSheetsDemo.ipynb
|   |   |   |   |   |-- html_tag_reader.ipynb
|   |   |   |   |   |-- legacy_office_reader.ipynb
|   |   |   |   |   |-- MakeDemo.ipynb
|   |   |   |   |   |-- MboxReaderDemo.ipynb
|   |   |   |   |   |-- MilvusReaderDemo.ipynb
|   |   |   |   |   |-- MongoDemo.ipynb
|   |   |   |   |   |-- MyScaleReaderDemo.ipynb
|   |   |   |   |   |-- NotionDemo.ipynb
|   |   |   |   |   |-- ObsidianReaderDemo.ipynb
|   |   |   |   |   |-- oracleai.ipynb
|   |   |   |   |   |-- OxylabsDemo.ipynb
|   |   |   |   |   |-- PathwayReaderDemo.ipynb
|   |   |   |   |   |-- PreprocessReaderDemo.ipynb
|   |   |   |   |   |-- PsychicDemo.ipynb
|   |   |   |   |   |-- QdrantDemo.ipynb
|   |   |   |   |   |-- simple_directory_reader.ipynb
|   |   |   |   |   |-- simple_directory_reader_parallel.ipynb
|   |   |   |   |   |-- simple_directory_reader_remote_fs.ipynb
|   |   |   |   |   |-- SlackDemo.ipynb
|   |   |   |   |   |-- TwitterDemo.ipynb
|   |   |   |   |   |-- WeaviateDemo.ipynb
|   |   |   |   |   |-- WebPageDemo.ipynb
|   |   |   |   |   \-- ZyteSerpDemo.ipynb
|   |   |   |   |-- discover_llamaindex
|   |   |   |   |   \-- document_management
|   |   |   |   |       |-- discord_dumps
|   |   |   |   |       |   |-- help_channel_dump_05_25_23.json
|   |   |   |   |       |   \-- help_channel_dump_06_02_23.json
|   |   |   |   |       |-- Discord_Thread_Management.ipynb
|   |   |   |   |       \-- group_conversations.py
|   |   |   |   |-- docstore
|   |   |   |   |   |-- AlloyDBDocstoreDemo.ipynb
|   |   |   |   |   |-- AzureDocstoreDemo.ipynb
|   |   |   |   |   |-- CloudSQLPgDocstoreDemo.ipynb
|   |   |   |   |   |-- DocstoreDemo.ipynb
|   |   |   |   |   |-- DynamoDBDocstoreDemo.ipynb
|   |   |   |   |   |-- FirestoreDemo.ipynb
|   |   |   |   |   |-- MongoDocstoreDemo.ipynb
|   |   |   |   |   |-- RedisDocstoreIndexStoreDemo.ipynb
|   |   |   |   |   \-- TablestoreDocstoreDemo.ipynb
|   |   |   |   |-- embeddings
|   |   |   |   |   |-- alephalpha.ipynb
|   |   |   |   |   |-- Anyscale.ipynb
|   |   |   |   |   |-- baseten.ipynb
|   |   |   |   |   |-- bedrock.ipynb
|   |   |   |   |   |-- clarifai.ipynb
|   |   |   |   |   |-- cloudflare_workersai.ipynb
|   |   |   |   |   |-- cohereai.ipynb
|   |   |   |   |   |-- custom_embeddings.ipynb
|   |   |   |   |   |-- dashscope_embeddings.ipynb
|   |   |   |   |   |-- databricks.ipynb
|   |   |   |   |   |-- deepinfra.ipynb
|   |   |   |   |   |-- elasticsearch.ipynb
|   |   |   |   |   |-- fastembed.ipynb
|   |   |   |   |   |-- fireworks.ipynb
|   |   |   |   |   |-- gemini.ipynb
|   |   |   |   |   |-- gigachat.ipynb
|   |   |   |   |   |-- google_genai.ipynb
|   |   |   |   |   |-- google_palm.ipynb
|   |   |   |   |   |-- heroku.ipynb
|   |   |   |   |   |-- huggingface.ipynb
|   |   |   |   |   |-- ibm_watsonx.ipynb
|   |   |   |   |   |-- ipex_llm.ipynb
|   |   |   |   |   |-- ipex_llm_gpu.ipynb
|   |   |   |   |   |-- isaacus.ipynb
|   |   |   |   |   |-- jina_embeddings.ipynb
|   |   |   |   |   |-- jinaai_embeddings.ipynb
|   |   |   |   |   |-- Langchain.ipynb
|   |   |   |   |   |-- llamafile.ipynb
|   |   |   |   |   |-- llm_rails.ipynb
|   |   |   |   |   |-- mistralai.ipynb
|   |   |   |   |   |-- mixedbreadai.ipynb
|   |   |   |   |   |-- modelscope.ipynb
|   |   |   |   |   |-- nebius.ipynb
|   |   |   |   |   |-- netmind.ipynb
|   |   |   |   |   |-- nomic.ipynb
|   |   |   |   |   |-- nvidia.ipynb
|   |   |   |   |   |-- oci_data_science.ipynb
|   |   |   |   |   |-- oci_genai.ipynb
|   |   |   |   |   |-- ollama_embedding.ipynb
|   |   |   |   |   |-- OpenAI.ipynb
|   |   |   |   |   |-- openvino.ipynb
|   |   |   |   |   |-- optimum_intel.ipynb
|   |   |   |   |   |-- oracleai.ipynb
|   |   |   |   |   |-- premai.ipynb
|   |   |   |   |   |-- sagemaker_embedding_endpoint.ipynb
|   |   |   |   |   |-- text_embedding_inference.ipynb
|   |   |   |   |   |-- textembed.ipynb
|   |   |   |   |   |-- together.ipynb
|   |   |   |   |   |-- upstage.ipynb
|   |   |   |   |   |-- vertex_embedding_endpoint.ipynb
|   |   |   |   |   |-- voyageai.ipynb
|   |   |   |   |   \-- yandexgpt.ipynb
|   |   |   |   |-- evaluation
|   |   |   |   |   |-- multi_modal
|   |   |   |   |   |   \-- multi_modal_rag_evaluation.ipynb
|   |   |   |   |   |-- retrieval
|   |   |   |   |   |   \-- retriever_eval.ipynb
|   |   |   |   |   |-- test_wiki_data
|   |   |   |   |   |   \-- nyc_text.txt
|   |   |   |   |   |-- AIMon.ipynb
|   |   |   |   |   |-- answer_and_context_relevancy.ipynb
|   |   |   |   |   |-- batch_eval.ipynb
|   |   |   |   |   |-- BeirEvaluation.ipynb
|   |   |   |   |   |-- Cleanlab.ipynb
|   |   |   |   |   |-- correctness_eval.ipynb
|   |   |   |   |   |-- Deepeval.ipynb
|   |   |   |   |   |-- faithfulness_eval.ipynb
|   |   |   |   |   |-- guideline_eval.ipynb
|   |   |   |   |   |-- HotpotQADistractor.ipynb
|   |   |   |   |   |-- mt_bench_human_judgement.ipynb
|   |   |   |   |   |-- mt_bench_single_grading.ipynb
|   |   |   |   |   |-- pairwise_eval.ipynb
|   |   |   |   |   |-- prometheus_evaluation.ipynb
|   |   |   |   |   |-- QuestionGeneration.ipynb
|   |   |   |   |   |-- RAGChecker.ipynb
|   |   |   |   |   |-- relevancy_eval.ipynb
|   |   |   |   |   |-- RetryQuery.ipynb
|   |   |   |   |   |-- semantic_similarity_eval.ipynb
|   |   |   |   |   |-- step_back_argilla.ipynb
|   |   |   |   |   |-- TonicValidateEvaluators.ipynb
|   |   |   |   |   \-- UpTrain.ipynb
|   |   |   |   |-- finetuning
|   |   |   |   |   |-- cross_encoder_finetuning
|   |   |   |   |   |   \-- cross_encoder_finetuning.ipynb
|   |   |   |   |   |-- embeddings
|   |   |   |   |   |   |-- eval_utils.py
|   |   |   |   |   |   |-- finetune_corpus_embedding.ipynb
|   |   |   |   |   |   |-- finetune_embedding.ipynb
|   |   |   |   |   |   \-- finetune_embedding_adapter.ipynb
|   |   |   |   |   |-- llm_judge
|   |   |   |   |   |   |-- correctness
|   |   |   |   |   |   |   \-- finetune_llm_judge_single_grading_correctness.ipynb
|   |   |   |   |   |   \-- pairwise
|   |   |   |   |   |       \-- finetune_llm_judge.ipynb
|   |   |   |   |   |-- react_agent
|   |   |   |   |   |   |-- eval_questions_10q.txt
|   |   |   |   |   |   |-- finetuning_events_10q.jsonl
|   |   |   |   |   |   \-- train_questions_10q.txt
|   |   |   |   |   |-- rerankers
|   |   |   |   |   |   \-- cohere_custom_reranker.ipynb
|   |   |   |   |   |-- router
|   |   |   |   |   |   \-- router_finetune.ipynb
|   |   |   |   |   |-- eval_questions.txt
|   |   |   |   |   |-- finetuning_events.jsonl
|   |   |   |   |   |-- mistralai_fine_tuning.ipynb
|   |   |   |   |   |-- openai_fine_tuning.ipynb
|   |   |   |   |   |-- openai_fine_tuning_functions.ipynb
|   |   |   |   |   \-- train_questions.txt
|   |   |   |   |-- graph_rag
|   |   |   |   |   \-- llama_index_cognee_integration.ipynb
|   |   |   |   |-- index_structs
|   |   |   |   |   |-- doc_summary
|   |   |   |   |   |   \-- DocSummary.ipynb
|   |   |   |   |   |-- knowledge_graph
|   |   |   |   |   |   |-- storage
|   |   |   |   |   |   |   \-- graph_store.json
|   |   |   |   |   |   |-- 2023_Science_Wikipedia_KnowledgeGraph.html
|   |   |   |   |   |   |-- example.html
|   |   |   |   |   |   |-- falkordbgraph_draw.html
|   |   |   |   |   |   |-- FalkorDBGraphDemo.ipynb
|   |   |   |   |   |   |-- index_kg.json
|   |   |   |   |   |   |-- index_kg_embeddings.json
|   |   |   |   |   |   |-- knowledge_graph2.ipynb
|   |   |   |   |   |   |-- KnowledgeGraphDemo.ipynb
|   |   |   |   |   |   |-- kuzugraph_draw.html
|   |   |   |   |   |   |-- nebulagraph_draw.html
|   |   |   |   |   |   |-- NebulaGraphKGIndexDemo.ipynb
|   |   |   |   |   |   |-- Neo4jKGIndexDemo.ipynb
|   |   |   |   |   |   |-- NeptuneDatabaseKGIndexDemo.ipynb
|   |   |   |   |   |   \-- TiDBKGIndexDemo.ipynb
|   |   |   |   |   \-- struct_indices
|   |   |   |   |       |-- duckdb_sql_query.ipynb
|   |   |   |   |       \-- SQLIndexDemo.ipynb
|   |   |   |   |-- ingestion
|   |   |   |   |   |-- advanced_ingestion_pipeline.ipynb
|   |   |   |   |   |-- async_ingestion_pipeline.ipynb
|   |   |   |   |   |-- document_management_pipeline.ipynb
|   |   |   |   |   |-- ingestion_gdrive.ipynb
|   |   |   |   |   |-- parallel_execution_ingestion_pipeline.ipynb
|   |   |   |   |   |-- ray_ingestion_pipeline.ipynb
|   |   |   |   |   \-- redis_ingestion_pipeline.ipynb
|   |   |   |   |-- instrumentation
|   |   |   |   |   |-- basic_usage.ipynb
|   |   |   |   |   |-- instrumentation_observability_rundown.ipynb
|   |   |   |   |   \-- observe_api_calls.ipynb
|   |   |   |   |-- llama_cloud
|   |   |   |   |   \-- figure_retrieval.ipynb
|   |   |   |   |-- llama_dataset
|   |   |   |   |   |-- downloading_llama_datasets.ipynb
|   |   |   |   |   |-- labelled-rag-datasets.ipynb
|   |   |   |   |   |-- ragdataset_submission_template.ipynb
|   |   |   |   |   \-- uploading_llama_dataset.ipynb
|   |   |   |   |-- llama_hub
|   |   |   |   |   |-- llama_hub.ipynb
|   |   |   |   |   |-- llama_pack_ollama.ipynb
|   |   |   |   |   |-- llama_pack_resume.ipynb
|   |   |   |   |   \-- llama_packs_example.ipynb
|   |   |   |   |-- llm
|   |   |   |   |   |-- ai21.ipynb
|   |   |   |   |   |-- alephalpha.ipynb
|   |   |   |   |   |-- anthropic.ipynb
|   |   |   |   |   |-- anthropic_prompt_caching.ipynb
|   |   |   |   |   |-- anyscale.ipynb
|   |   |   |   |   |-- apertis.ipynb
|   |   |   |   |   |-- asi1.ipynb
|   |   |   |   |   |-- azure_env.png
|   |   |   |   |   |-- azure_inference.ipynb
|   |   |   |   |   |-- azure_openai.ipynb
|   |   |   |   |   |-- azure_playground.png
|   |   |   |   |   |-- baseten.ipynb
|   |   |   |   |   |-- bedrock.ipynb
|   |   |   |   |   |-- bedrock_converse.ipynb
|   |   |   |   |   |-- cerebras.ipynb
|   |   |   |   |   |-- clarifai.ipynb
|   |   |   |   |   |-- cleanlab.ipynb
|   |   |   |   |   |-- cohere.ipynb
|   |   |   |   |   |-- cometapi.ipynb
|   |   |   |   |   |-- dashscope.ipynb
|   |   |   |   |   |-- databricks.ipynb
|   |   |   |   |   |-- deepinfra.ipynb
|   |   |   |   |   |-- deepseek.ipynb
|   |   |   |   |   |-- everlyai.ipynb
|   |   |   |   |   |-- featherlessai.ipynb
|   |   |   |   |   |-- fireworks.ipynb
|   |   |   |   |   |-- fireworks_cookbook.ipynb
|   |   |   |   |   |-- friendli.ipynb
|   |   |   |   |   |-- gemini.ipynb
|   |   |   |   |   |-- google_genai.ipynb
|   |   |   |   |   |-- grok.ipynb
|   |   |   |   |   |-- groq.ipynb
|   |   |   |   |   |-- helicone.ipynb
|   |   |   |   |   |-- heroku.ipynb
|   |   |   |   |   |-- huggingface.ipynb
|   |   |   |   |   |-- ibm_watsonx.ipynb
|   |   |   |   |   |-- ipex_llm.ipynb
|   |   |   |   |   |-- ipex_llm_gpu.ipynb
|   |   |   |   |   |-- konko.ipynb
|   |   |   |   |   |-- langchain.ipynb
|   |   |   |   |   |-- litellm.ipynb
|   |   |   |   |   |-- llama_2.ipynb
|   |   |   |   |   |-- llama_2_rap_battle.ipynb
|   |   |   |   |   |-- llama_api.ipynb
|   |   |   |   |   |-- llama_cpp.ipynb
|   |   |   |   |   |-- llama_paradise.png
|   |   |   |   |   |-- llamafile.ipynb
|   |   |   |   |   |-- llm_predictor.ipynb
|   |   |   |   |   |-- lmstudio.ipynb
|   |   |   |   |   |-- localai.ipynb
|   |   |   |   |   |-- maritalk.ipynb
|   |   |   |   |   |-- mistral_rs.ipynb
|   |   |   |   |   |-- mistralai.ipynb
|   |   |   |   |   |-- modelscope.ipynb
|   |   |   |   |   |-- monsterapi.ipynb
|   |   |   |   |   |-- mymagic.ipynb
|   |   |   |   |   |-- nebius.ipynb
|   |   |   |   |   |-- netmind.ipynb
|   |   |   |   |   |-- neutrino.ipynb
|   |   |   |   |   |-- nvidia.ipynb
|   |   |   |   |   |-- nvidia_nim.ipynb
|   |   |   |   |   |-- nvidia_tensorrt.ipynb
|   |   |   |   |   |-- nvidia_text_completion.ipynb
|   |   |   |   |   |-- nvidia_triton.ipynb
|   |   |   |   |   |-- oci_data_science.ipynb
|   |   |   |   |   |-- oci_genai.ipynb
|   |   |   |   |   |-- octoai.ipynb
|   |   |   |   |   |-- ollama.ipynb
|   |   |   |   |   |-- ollama_gemma.ipynb
|   |   |   |   |   |-- openai.ipynb
|   |   |   |   |   |-- openai_json_vs_function_calling.ipynb
|   |   |   |   |   |-- openai_responses.ipynb
|   |   |   |   |   |-- openrouter.ipynb
|   |   |   |   |   |-- openvino-genai.ipynb
|   |   |   |   |   |-- openvino.ipynb
|   |   |   |   |   |-- optimum_intel.ipynb
|   |   |   |   |   |-- opus_4_1.ipynb
|   |   |   |   |   |-- paieas.ipynb
|   |   |   |   |   |-- palm.ipynb
|   |   |   |   |   |-- perplexity.ipynb
|   |   |   |   |   |-- pipeshift.ipynb
|   |   |   |   |   |-- portkey.ipynb
|   |   |   |   |   |-- predibase.ipynb
|   |   |   |   |   |-- premai.ipynb
|   |   |   |   |   |-- qianfan.ipynb
|   |   |   |   |   |-- rungpt.ipynb
|   |   |   |   |   |-- sagemaker_endpoint_llm.ipynb
|   |   |   |   |   |-- sambanovasystems.ipynb
|   |   |   |   |   |-- together.ipynb
|   |   |   |   |   |-- upstage.ipynb
|   |   |   |   |   |-- vercel-ai-gateway.ipynb
|   |   |   |   |   |-- vertex.ipynb
|   |   |   |   |   |-- vicuna.ipynb
|   |   |   |   |   |-- vllm.ipynb
|   |   |   |   |   |-- xinference_local_deployment.ipynb
|   |   |   |   |   \-- yi.ipynb
|   |   |   |   |-- low_level
|   |   |   |   |   |-- evaluation.ipynb
|   |   |   |   |   |-- fusion_retriever.ipynb
|   |   |   |   |   |-- ingestion.ipynb
|   |   |   |   |   |-- oss_ingestion_retrieval.ipynb
|   |   |   |   |   |-- response_synthesis.ipynb
|   |   |   |   |   |-- retrieval.ipynb
|   |   |   |   |   |-- router.ipynb
|   |   |   |   |   \-- vector_store.ipynb
|   |   |   |   |-- managed
|   |   |   |   |   |-- BGEM3Demo.ipynb
|   |   |   |   |   |-- GoogleDemo.ipynb
|   |   |   |   |   |-- manage_retrieval_benchmark.ipynb
|   |   |   |   |   |-- PostgresMLDemo.ipynb
|   |   |   |   |   |-- vectaraDemo.ipynb
|   |   |   |   |   \-- VertexAIDemo.ipynb
|   |   |   |   |-- memory
|   |   |   |   |   |-- agentcore_memory_sample.ipynb
|   |   |   |   |   |-- ChatSummaryMemoryBuffer.ipynb
|   |   |   |   |   |-- custom_memory.ipynb
|   |   |   |   |   |-- custom_multi_turn_memory.ipynb
|   |   |   |   |   |-- Mem0Memory.ipynb
|   |   |   |   |   \-- memory.ipynb
|   |   |   |   |-- metadata_extraction
|   |   |   |   |   |-- data
|   |   |   |   |   |   \-- Sports Supplements.csv
|   |   |   |   |   |-- DocumentContextExtractor.ipynb
|   |   |   |   |   |-- EntityExtractionClimate.ipynb
|   |   |   |   |   |-- MarvinMetadataExtractorDemo.ipynb
|   |   |   |   |   |-- MetadataExtraction_LLMSurvey.ipynb
|   |   |   |   |   |-- MetadataExtractionSEC.ipynb
|   |   |   |   |   \-- PydanticExtractor.ipynb
|   |   |   |   |-- multi_modal
|   |   |   |   |   |-- anthropic_multi_modal.ipynb
|   |   |   |   |   |-- azure_openai_multi_modal.ipynb
|   |   |   |   |   |-- ChromaMultiModalDemo.ipynb
|   |   |   |   |   |-- cohere_multi_modal.ipynb
|   |   |   |   |   |-- dashscope_multi_modal.ipynb
|   |   |   |   |   |-- gemini.ipynb
|   |   |   |   |   |-- gpt4o_mm_structured_outputs.ipynb
|   |   |   |   |   |-- gpt4v_experiments_cot.ipynb
|   |   |   |   |   |-- gpt4v_multi_modal_retrieval.ipynb
|   |   |   |   |   |-- image_to_image_retrieval.ipynb
|   |   |   |   |   |-- llamaindex_mongodb_voyageai_multimodal.ipynb
|   |   |   |   |   |-- llava_demo.ipynb
|   |   |   |   |   |-- llava_multi_modal_tesla_10q.ipynb
|   |   |   |   |   |-- mistral_multi_modal.ipynb
|   |   |   |   |   |-- multi_modal_pydantic.ipynb
|   |   |   |   |   |-- multi_modal_rag_nomic.ipynb
|   |   |   |   |   |-- multi_modal_retrieval.ipynb
|   |   |   |   |   |-- multi_modal_video_RAG.ipynb
|   |   |   |   |   |-- multi_modal_videorag_videodb.ipynb
|   |   |   |   |   |-- multimodal_rag_guardrail_gemini_llmguard_llmguard.ipynb
|   |   |   |   |   |-- nebius_multi_modal.ipynb
|   |   |   |   |   |-- nvidia_multi_modal.ipynb
|   |   |   |   |   |-- openai_multi_modal.ipynb
|   |   |   |   |   |-- openvino_multimodal.ipynb
|   |   |   |   |   |-- replicate_multi_modal.ipynb
|   |   |   |   |   \-- structured_image_retrieval.ipynb
|   |   |   |   |-- multi_tenancy
|   |   |   |   |   \-- multi_tenancy_rag.ipynb
|   |   |   |   |-- node_parsers
|   |   |   |   |   |-- code_splitter_chunking.ipynb
|   |   |   |   |   |-- semantic_chunking.ipynb
|   |   |   |   |   |-- semantic_double_merging_chunking.ipynb
|   |   |   |   |   |-- slide_parser.ipynb
|   |   |   |   |   \-- topic_parser.ipynb
|   |   |   |   |-- node_postprocessor
|   |   |   |   |   |-- AIMonRerank.ipynb
|   |   |   |   |   |-- CohereRerank.ipynb
|   |   |   |   |   |-- ColbertRerank.ipynb
|   |   |   |   |   |-- ColPaliRerank.ipynb
|   |   |   |   |   |-- FileNodeProcessors.ipynb
|   |   |   |   |   |-- FlagEmbeddingReranker.ipynb
|   |   |   |   |   |-- ibm_watsonx.ipynb
|   |   |   |   |   |-- index_recency_test.json
|   |   |   |   |   |-- JinaRerank.ipynb
|   |   |   |   |   |-- LLMReranker-Gatsby.ipynb
|   |   |   |   |   |-- LLMReranker-Lyft-10k.ipynb
|   |   |   |   |   |-- LongContextReorder.ipynb
|   |   |   |   |   |-- MetadataReplacementDemo.ipynb
|   |   |   |   |   |-- MixedbreadAIRerank.ipynb
|   |   |   |   |   |-- NVIDIARerank.ipynb
|   |   |   |   |   |-- openvino_rerank.ipynb
|   |   |   |   |   |-- OptimizerDemo.ipynb
|   |   |   |   |   |-- PII.ipynb
|   |   |   |   |   |-- PrevNextPostprocessorDemo.ipynb
|   |   |   |   |   |-- rankGPT.ipynb
|   |   |   |   |   |-- rankLLM.ipynb
|   |   |   |   |   |-- RecencyPostprocessorDemo.ipynb
|   |   |   |   |   |-- SentenceTransformerRerank.ipynb
|   |   |   |   |   |-- Structured-LLMReranker-Lyft-10k.ipynb
|   |   |   |   |   |-- TimeWeightedPostprocessorDemo.ipynb
|   |   |   |   |   \-- VoyageAIRerank.ipynb
|   |   |   |   |-- objects
|   |   |   |   |   \-- object_index.ipynb
|   |   |   |   |-- observability
|   |   |   |   |   |-- img
|   |   |   |   |   |   |-- dashboard-posthog-1.png
|   |   |   |   |   |   |-- dashboard-posthog-2.png
|   |   |   |   |   |   \-- integration-posthog-llamaindex-mistral.png
|   |   |   |   |   |-- AimCallback.ipynb
|   |   |   |   |   |-- Deepeval.ipynb
|   |   |   |   |   |-- HoneyHiveLlamaIndexTracer.ipynb
|   |   |   |   |   |-- Langfuse-Instrumentation.ipynb
|   |   |   |   |   |-- LangfuseCallbackHandler.ipynb
|   |   |   |   |   |-- LangfuseMistralPostHog.ipynb
|   |   |   |   |   |-- LlamaDebugHandler.ipynb
|   |   |   |   |   |-- Maxim-Instrumentation.ipynb
|   |   |   |   |   |-- MLflow.ipynb
|   |   |   |   |   |-- OpenInferenceCallback.ipynb
|   |   |   |   |   |-- OpenLLMetry.ipynb
|   |   |   |   |   |-- OpikCallback.ipynb
|   |   |   |   |   |-- PromptLayerHandler.ipynb
|   |   |   |   |   |-- TokenCountingHandler.ipynb
|   |   |   |   |   |-- UpTrainCallback.ipynb
|   |   |   |   |   \-- WandbCallbackHandler.ipynb
|   |   |   |   |-- output_parsing
|   |   |   |   |   |-- df_program.ipynb
|   |   |   |   |   |-- directory.py
|   |   |   |   |   |-- evaporate_program.ipynb
|   |   |   |   |   |-- function_program.ipynb
|   |   |   |   |   |-- GuardrailsDemo.ipynb
|   |   |   |   |   |-- guidance_pydantic_program.ipynb
|   |   |   |   |   |-- guidance_sub_question.ipynb
|   |   |   |   |   |-- LangchainOutputParserDemo.ipynb
|   |   |   |   |   |-- llm_program.ipynb
|   |   |   |   |   |-- lmformatenforcer_pydantic_program.ipynb
|   |   |   |   |   |-- lmformatenforcer_regular_expressions.ipynb
|   |   |   |   |   |-- nvidia_output_parsing.ipynb
|   |   |   |   |   |-- openai_pydantic_program.ipynb
|   |   |   |   |   \-- openai_sub_question.ipynb
|   |   |   |   |-- param_optimizer
|   |   |   |   |   \-- param_optimizer.ipynb
|   |   |   |   |-- prompts
|   |   |   |   |   |-- advanced_prompts.ipynb
|   |   |   |   |   |-- emotion_prompt.ipynb
|   |   |   |   |   |-- llama2_qa_citation_events.jsonl
|   |   |   |   |   |-- prompt_mixin.ipynb
|   |   |   |   |   |-- rich_prompt_template_features.ipynb
|   |   |   |   |   \-- structured_input.ipynb
|   |   |   |   |-- property_graph
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- agentic_graph_rag_vertex.ipynb
|   |   |   |   |   |-- Dynamic_KG_Extraction.ipynb
|   |   |   |   |   |-- graph_store.ipynb
|   |   |   |   |   |-- jupyter_screenshot.png
|   |   |   |   |   |-- kg_screenshot.png
|   |   |   |   |   |-- local_kg.png
|   |   |   |   |   |-- low_level_graph.png
|   |   |   |   |   |-- property_graph_advanced.ipynb
|   |   |   |   |   |-- property_graph_basic.ipynb
|   |   |   |   |   |-- property_graph_basic_visualization.ipynb
|   |   |   |   |   |-- property_graph_custom_retriever.ipynb
|   |   |   |   |   |-- property_graph_falkordb.ipynb
|   |   |   |   |   |-- property_graph_memgraph.ipynb
|   |   |   |   |   |-- property_graph_nebula.ipynb
|   |   |   |   |   |-- property_graph_neo4j.ipynb
|   |   |   |   |   |-- property_graph_neptune.ipynb
|   |   |   |   |   \-- property_graph_tidb.ipynb
|   |   |   |   |-- query_engine
|   |   |   |   |   |-- multi_doc_auto_retrieval
|   |   |   |   |   |   \-- multi_doc_auto_retrieval.ipynb
|   |   |   |   |   |-- pdf_tables
|   |   |   |   |   |   |-- billionaires_page.pdf
|   |   |   |   |   |   \-- recursive_retriever.ipynb
|   |   |   |   |   |-- sec_tables
|   |   |   |   |   |   \-- tesla_10q_table.ipynb
|   |   |   |   |   |-- citation_query_engine.ipynb
|   |   |   |   |   |-- cogniswitch_query_engine.ipynb
|   |   |   |   |   |-- custom_query_engine.ipynb
|   |   |   |   |   |-- CustomRetrievers.ipynb
|   |   |   |   |   |-- ensemble_query_engine.ipynb
|   |   |   |   |   |-- flare_query_engine.ipynb
|   |   |   |   |   |-- JointQASummary.ipynb
|   |   |   |   |   |-- json_query_engine.ipynb
|   |   |   |   |   |-- JSONalyze_query_engine.ipynb
|   |   |   |   |   |-- knowledge_graph_query_engine.ipynb
|   |   |   |   |   |-- knowledge_graph_rag_query_engine.ipynb
|   |   |   |   |   |-- nebulagraph_draw.html
|   |   |   |   |   |-- nebulagraph_draw_quill.html
|   |   |   |   |   |-- pandas_query_engine.ipynb
|   |   |   |   |   |-- pgvector_sql_query_engine.ipynb
|   |   |   |   |   |-- polars_query_engine.ipynb
|   |   |   |   |   |-- pydantic_query_engine.ipynb
|   |   |   |   |   |-- RetrieverRouterQueryEngine.ipynb
|   |   |   |   |   |-- RouterQueryEngine.ipynb
|   |   |   |   |   |-- SQLAutoVectorQueryEngine.ipynb
|   |   |   |   |   |-- SQLJoinQueryEngine.ipynb
|   |   |   |   |   |-- SQLRouterQueryEngine.ipynb
|   |   |   |   |   \-- sub_question_query_engine.ipynb
|   |   |   |   |-- query_transformations
|   |   |   |   |   |-- HyDEQueryTransformDemo.ipynb
|   |   |   |   |   |-- query_transform_cookbook.ipynb
|   |   |   |   |   \-- SimpleIndexDemo-multistep.ipynb
|   |   |   |   |-- response_synthesizers
|   |   |   |   |   |-- custom_prompt_synthesizer.ipynb
|   |   |   |   |   |-- long_context_test.ipynb
|   |   |   |   |   |-- pydantic_tree_summarize.ipynb
|   |   |   |   |   |-- refine.ipynb
|   |   |   |   |   |-- structured_refine.ipynb
|   |   |   |   |   \-- tree_summarize.ipynb
|   |   |   |   |-- retrievers
|   |   |   |   |   |-- data
|   |   |   |   |   |   \-- paul_graham
|   |   |   |   |   |       \-- paul_graham_essay.txt
|   |   |   |   |   |-- auto_merging_retriever.ipynb
|   |   |   |   |   |-- auto_vs_recursive_retriever.ipynb
|   |   |   |   |   |-- bedrock_retriever.ipynb
|   |   |   |   |   |-- bm25_retriever.ipynb
|   |   |   |   |   |-- composable_retrievers.ipynb
|   |   |   |   |   |-- deep_memory.ipynb
|   |   |   |   |   |-- ensemble_retrieval.ipynb
|   |   |   |   |   |-- multi_doc_together_hybrid.ipynb
|   |   |   |   |   |-- pathway_retriever.ipynb
|   |   |   |   |   |-- reciprocal_rerank_fusion.ipynb
|   |   |   |   |   |-- recurisve_retriever_nodes_braintrust.ipynb
|   |   |   |   |   |-- recursive_retriever_nodes.ipynb
|   |   |   |   |   |-- relative_score_dist_fusion.ipynb
|   |   |   |   |   |-- router_retriever.ipynb
|   |   |   |   |   |-- simple_fusion.ipynb
|   |   |   |   |   |-- vectara_auto_retriever.ipynb
|   |   |   |   |   |-- vertex_ai_search_retriever.ipynb
|   |   |   |   |   |-- videodb_retriever.ipynb
|   |   |   |   |   \-- you_retriever.ipynb
|   |   |   |   |-- selectors
|   |   |   |   |   \-- not_diamond_selector.ipynb
|   |   |   |   |-- structured_outputs
|   |   |   |   |   \-- structured_outputs.ipynb
|   |   |   |   |-- tools
|   |   |   |   |   |-- AgentQL_browser_agent.ipynb
|   |   |   |   |   |-- azure_code_interpreter.ipynb
|   |   |   |   |   |-- cassandra.ipynb
|   |   |   |   |   |-- eval_query_engine_tool.ipynb
|   |   |   |   |   |-- function_tool_callback.ipynb
|   |   |   |   |   |-- mcp.ipynb
|   |   |   |   |   |-- mcp_agent_tools.ipynb
|   |   |   |   |   |-- mcp_toolbox.ipynb
|   |   |   |   |   |-- moss_with_llamaindex.ipynb
|   |   |   |   |   |-- OnDemandLoaderTool.ipynb
|   |   |   |   |   |-- order_completion_agent_with_artifact_editor.ipynb
|   |   |   |   |   \-- Use_Klavis_with_LlamaIndex.ipynb
|   |   |   |   |-- transforms
|   |   |   |   |   \-- TransformsEval.ipynb
|   |   |   |   |-- usecases
|   |   |   |   |   |-- 10k_sub_question.ipynb
|   |   |   |   |   |-- 10q_sub_question.ipynb
|   |   |   |   |   |-- email_data_extraction.ipynb
|   |   |   |   |   |-- fastapi_rag_ollama.ipynb
|   |   |   |   |   |-- github_issue_analysis.ipynb
|   |   |   |   |   \-- github_issue_analysis_data.pkl
|   |   |   |   |-- vector_stores
|   |   |   |   |   |-- existing_data
|   |   |   |   |   |   |-- pinecone_existing_data.ipynb
|   |   |   |   |   |   \-- weaviate_existing_data.ipynb
|   |   |   |   |   |-- AlibabaCloudMySQLDemo.ipynb
|   |   |   |   |   |-- AlibabaCloudOpenSearchIndexDemo.ipynb
|   |   |   |   |   |-- AlloyDBVectorStoreDemo.ipynb
|   |   |   |   |   |-- AmazonNeptuneVectorDemo.ipynb
|   |   |   |   |   |-- AnalyticDBDemo.ipynb
|   |   |   |   |   |-- ApertureDBVectorStoreDemo.ipynb
|   |   |   |   |   |-- AstraDBIndexDemo.ipynb
|   |   |   |   |   |-- AsyncIndexCreationDemo.ipynb
|   |   |   |   |   |-- AwadbDemo.ipynb
|   |   |   |   |   |-- AWSDocDBDemo.ipynb
|   |   |   |   |   |-- AzureAISearchIndexDemo.ipynb
|   |   |   |   |   |-- AzureCosmosDBMongoDBvCoreDemo.ipynb
|   |   |   |   |   |-- AzureCosmosDBNoSqlDemo.ipynb
|   |   |   |   |   |-- azurepostgresql.ipynb
|   |   |   |   |   |-- BagelAutoRetriever.ipynb
|   |   |   |   |   |-- BagelIndexDemo.ipynb
|   |   |   |   |   |-- BaiduVectorDBIndexDemo.ipynb
|   |   |   |   |   |-- CassandraIndexDemo.ipynb
|   |   |   |   |   |-- chroma_auto_retriever.ipynb
|   |   |   |   |   |-- chroma_metadata_filter.ipynb
|   |   |   |   |   |-- ChromaFireworksNomic.ipynb
|   |   |   |   |   |-- ChromaIndexDemo.ipynb
|   |   |   |   |   |-- ClickHouseIndexDemo.ipynb
|   |   |   |   |   |-- CloudSQLPgVectorStoreDemo.ipynb
|   |   |   |   |   |-- CouchbaseVectorStoreDemo.ipynb
|   |   |   |   |   |-- DashvectorIndexDemo.ipynb
|   |   |   |   |   |-- DatabricksVectorSearchDemo.ipynb
|   |   |   |   |   |-- db2llamavs.ipynb
|   |   |   |   |   |-- DeepLakeIndexDemo.ipynb
|   |   |   |   |   |-- DocArrayHnswIndexDemo.ipynb
|   |   |   |   |   |-- DocArrayInMemoryIndexDemo.ipynb
|   |   |   |   |   |-- DragonflyIndexDemo.ipynb
|   |   |   |   |   |-- DuckDBDemo.ipynb
|   |   |   |   |   |-- elasticsearch_auto_retriever.ipynb
|   |   |   |   |   |-- Elasticsearch_demo.ipynb
|   |   |   |   |   |-- ElasticsearchIndexDemo.ipynb
|   |   |   |   |   |-- EpsillaIndexDemo.ipynb
|   |   |   |   |   |-- FaissIndexDemo.ipynb
|   |   |   |   |   |-- FirestoreVectorStore.ipynb
|   |   |   |   |   |-- gel.ipynb
|   |   |   |   |   |-- HnswlibIndexDemo.ipynb
|   |   |   |   |   |-- HologresDemo.ipynb
|   |   |   |   |   |-- index_faiss.json
|   |   |   |   |   |-- index_faiss_core.index
|   |   |   |   |   |-- index_simple.json
|   |   |   |   |   |-- JaguarIndexDemo.ipynb
|   |   |   |   |   |-- KDBAI_Advanced_RAG_Demo.ipynb
|   |   |   |   |   |-- LanceDBIndexDemo.ipynb
|   |   |   |   |   |-- LanternAutoRetriever.ipynb
|   |   |   |   |   |-- LanternIndexDemo.ipynb
|   |   |   |   |   |-- LindormDemo.ipynb
|   |   |   |   |   |-- MilvusAsyncAPIDemo.ipynb
|   |   |   |   |   |-- MilvusFullTextSearchDemo.ipynb
|   |   |   |   |   |-- MilvusHybridIndexDemo.ipynb
|   |   |   |   |   |-- MilvusIndexDemo.ipynb
|   |   |   |   |   |-- MilvusOperatorFunctionDemo.ipynb
|   |   |   |   |   |-- MongoDBAtlasVectorSearch.ipynb
|   |   |   |   |   |-- MongoDBAtlasVectorSearchRAGFireworks.ipynb
|   |   |   |   |   |-- MongoDBAtlasVectorSearchRAGOpenAI.ipynb
|   |   |   |   |   |-- MoorchehDemo.ipynb
|   |   |   |   |   |-- MyScaleIndexDemo.ipynb
|   |   |   |   |   |-- neo4j_metadata_filter.ipynb
|   |   |   |   |   |-- Neo4jVectorDemo.ipynb
|   |   |   |   |   |-- NileVectorStore.ipynb
|   |   |   |   |   |-- ObjectBoxIndexDemo.ipynb
|   |   |   |   |   |-- OceanBaseVectorStore.ipynb
|   |   |   |   |   |-- OpensearchDemo.ipynb
|   |   |   |   |   |-- orallamavs.ipynb
|   |   |   |   |   |-- PGVectoRsDemo.ipynb
|   |   |   |   |   |-- pinecone_auto_retriever.ipynb
|   |   |   |   |   |-- pinecone_metadata_filter.ipynb
|   |   |   |   |   |-- PineconeIndexDemo-Hybrid.ipynb
|   |   |   |   |   |-- PineconeIndexDemo.ipynb
|   |   |   |   |   |-- postgres.ipynb
|   |   |   |   |   |-- qdrant_bm42.ipynb
|   |   |   |   |   |-- qdrant_hybrid.ipynb
|   |   |   |   |   |-- Qdrant_hybrid_rag_multitenant_sharding.ipynb
|   |   |   |   |   |-- Qdrant_metadata_filter.ipynb
|   |   |   |   |   |-- Qdrant_using_qdrant_filters.ipynb
|   |   |   |   |   |-- QdrantIndexDemo.ipynb
|   |   |   |   |   |-- RedisIndexDemo.ipynb
|   |   |   |   |   |-- RelytDemo.ipynb
|   |   |   |   |   |-- RocksetIndexDemo.ipynb
|   |   |   |   |   |-- S3VectorStore.ipynb
|   |   |   |   |   |-- SimpleIndexDemo.ipynb
|   |   |   |   |   |-- SimpleIndexDemoLlama-Local.ipynb
|   |   |   |   |   |-- SimpleIndexDemoLlama2.ipynb
|   |   |   |   |   |-- SimpleIndexDemoMMR.ipynb
|   |   |   |   |   |-- SimpleIndexOnS3.ipynb
|   |   |   |   |   |-- SupabaseVectorIndexDemo.ipynb
|   |   |   |   |   |-- TablestoreDemo.ipynb
|   |   |   |   |   |-- TairIndexDemo.ipynb
|   |   |   |   |   |-- TencentVectorDBIndexDemo.ipynb
|   |   |   |   |   |-- TiDBVector.ipynb
|   |   |   |   |   |-- Timescalevector.ipynb
|   |   |   |   |   |-- TxtaiIndexDemo.ipynb
|   |   |   |   |   |-- TypesenseDemo.ipynb
|   |   |   |   |   |-- UpstashVectorDemo.ipynb
|   |   |   |   |   |-- VearchDemo.ipynb
|   |   |   |   |   |-- VectorXDemo.ipynb
|   |   |   |   |   |-- VertexAIVectorSearchDemo.ipynb
|   |   |   |   |   |-- VertexAIVectorSearchV2Demo.ipynb
|   |   |   |   |   |-- VespaIndexDemo.ipynb
|   |   |   |   |   |-- WeaviateIndex_auto_retriever.ipynb
|   |   |   |   |   |-- WeaviateIndex_metadata_filter.ipynb
|   |   |   |   |   |-- WeaviateIndexDemo-Hybrid.ipynb
|   |   |   |   |   |-- WeaviateIndexDemo.ipynb
|   |   |   |   |   |-- WordLiftDemo.ipynb
|   |   |   |   |   \-- ZepIndexDemo.ipynb
|   |   |   |   |-- workflow
|   |   |   |   |   |-- advanced_text_to_sql.ipynb
|   |   |   |   |   |-- checkpointing_workflows.ipynb
|   |   |   |   |   |-- citation_query_engine.ipynb
|   |   |   |   |   |-- corrective_rag_pack.ipynb
|   |   |   |   |   |-- function_calling_agent.ipynb
|   |   |   |   |   |-- human_in_the_loop_story_crafting.ipynb
|   |   |   |   |   |-- JSONalyze_query_engine.ipynb
|   |   |   |   |   |-- long_rag_pack.ipynb
|   |   |   |   |   |-- multi_step_query_engine.ipynb
|   |   |   |   |   |-- multi_strategy_workflow.ipynb
|   |   |   |   |   |-- parallel_execution.ipynb
|   |   |   |   |   |-- planning_workflow.ipynb
|   |   |   |   |   |-- rag.ipynb
|   |   |   |   |   |-- react_agent.ipynb
|   |   |   |   |   |-- reflection.ipynb
|   |   |   |   |   |-- router_query_engine.ipynb
|   |   |   |   |   |-- self_discover_workflow.ipynb
|   |   |   |   |   |-- sub_question_query_engine.ipynb
|   |   |   |   |   \-- workflows_cookbook.ipynb
|   |   |   |   \-- index.md
|   |   |   |-- scripts
|   |   |   |   \-- prepare_for_build.py
|   |   |   |-- src
|   |   |   |   |-- assets
|   |   |   |   |   |-- llamaindex-dark.svg
|   |   |   |   |   |-- llamaindex-light.svg
|   |   |   |   |   \-- logo-chip-enormous.png
|   |   |   |   |-- components
|   |   |   |   |   |-- Header.astro
|   |   |   |   |   \-- SiteTitle.astro
|   |   |   |   |-- content
|   |   |   |   |   \-- docs
|   |   |   |   |       \-- framework
|   |   |   |   |           |-- _static
|   |   |   |   |           |   |-- agents
|   |   |   |   |           |   |   |-- agent_step_execute.png
|   |   |   |   |           |   |   \-- workflow-weaviate-multiagent.png
|   |   |   |   |           |   |-- assets
|   |   |   |   |           |   |   |-- LlamaLogoBrowserTab.png
|   |   |   |   |           |   |   \-- LlamaSquareBlack.svg
|   |   |   |   |           |   |-- composability
|   |   |   |   |           |   |   |-- diagram.png
|   |   |   |   |           |   |   |-- diagram_b0.png
|   |   |   |   |           |   |   |-- diagram_b1.png
|   |   |   |   |           |   |   |-- diagram_q1.png
|   |   |   |   |           |   |   \-- diagram_q2.png
|   |   |   |   |           |   |-- contribution
|   |   |   |   |           |   |   \-- contrib.png
|   |   |   |   |           |   |-- css
|   |   |   |   |           |   |   |-- algolia.css
|   |   |   |   |           |   |   \-- custom.css
|   |   |   |   |           |   |-- data_connectors
|   |   |   |   |           |   |   \-- llamahub.png
|   |   |   |   |           |   |-- embeddings
|   |   |   |   |           |   |   \-- doc_example.jpeg
|   |   |   |   |           |   |-- evaluation
|   |   |   |   |           |   |   |-- eval_query_response_context.png
|   |   |   |   |           |   |   |-- eval_query_sources.png
|   |   |   |   |           |   |   \-- eval_response_context.png
|   |   |   |   |           |   |-- getting_started
|   |   |   |   |           |   |   |-- basic_rag.png
|   |   |   |   |           |   |   |-- indexing.jpg
|   |   |   |   |           |   |   |-- querying.jpg
|   |   |   |   |           |   |   |-- rag.jpg
|   |   |   |   |           |   |   \-- stages.png
|   |   |   |   |           |   |-- indices
|   |   |   |   |           |   |   |-- create_and_refine.png
|   |   |   |   |           |   |   |-- keyword.png
|   |   |   |   |           |   |   |-- keyword_query.png
|   |   |   |   |           |   |   |-- list.png
|   |   |   |   |           |   |   |-- list_filter_query.png
|   |   |   |   |           |   |   |-- list_query.png
|   |   |   |   |           |   |   |-- tree.png
|   |   |   |   |           |   |   |-- tree_query.png
|   |   |   |   |           |   |   |-- tree_summarize.png
|   |   |   |   |           |   |   |-- vector_store.png
|   |   |   |   |           |   |   \-- vector_store_query.png
|   |   |   |   |           |   |-- integrations
|   |   |   |   |           |   |   |-- mlflow
|   |   |   |   |           |   |   |   |-- mlflow.gif
|   |   |   |   |           |   |   |   |-- mlflow_chat_trace_quickstart.png
|   |   |   |   |           |   |   |   |-- mlflow_query_trace_quickstart.png
|   |   |   |   |           |   |   |   |-- mlflow_run_quickstart.png
|   |   |   |   |           |   |   |   |-- mlflow_settings_quickstart.png
|   |   |   |   |           |   |   |   \-- mlflow_traces_list_quickstart.png
|   |   |   |   |           |   |   |-- weave
|   |   |   |   |           |   |   |   \-- weave_quickstart.png
|   |   |   |   |           |   |   |-- agenta.png
|   |   |   |   |           |   |   |-- argilla.png
|   |   |   |   |           |   |   |-- arize_phoenix.png
|   |   |   |   |           |   |   |-- honeyhive.png
|   |   |   |   |           |   |   |-- openllmetry.png
|   |   |   |   |           |   |   |-- opik.png
|   |   |   |   |           |   |   |-- perfetto.png
|   |   |   |   |           |   |   |-- tonic-validate-graph.png
|   |   |   |   |           |   |   |-- trulens.png
|   |   |   |   |           |   |   \-- wandb.png
|   |   |   |   |           |   |-- js
|   |   |   |   |           |   |   |-- algolia.js
|   |   |   |   |           |   |   |-- leadfeeder.js
|   |   |   |   |           |   |   \-- mendablesearch.js
|   |   |   |   |           |   |-- node_postprocessors
|   |   |   |   |           |   |   |-- prev_next.png
|   |   |   |   |           |   |   \-- recency.png
|   |   |   |   |           |   |-- production_rag
|   |   |   |   |           |   |   |-- decouple_chunks.png
|   |   |   |   |           |   |   |-- doc_agents.png
|   |   |   |   |           |   |   |-- joint_qa_summary.png
|   |   |   |   |           |   |   \-- structured_retrieval.png
|   |   |   |   |           |   |-- query
|   |   |   |   |           |   |   |-- disclosure.png
|   |   |   |   |           |   |   |-- pipeline_rag_example.png
|   |   |   |   |           |   |   \-- query_classes.png
|   |   |   |   |           |   |-- query_transformations
|   |   |   |   |           |   |   |-- multi_step_diagram.png
|   |   |   |   |           |   |   \-- single_step_diagram.png
|   |   |   |   |           |   |-- response
|   |   |   |   |           |   |   \-- response_1.jpeg
|   |   |   |   |           |   |-- storage
|   |   |   |   |           |   |   \-- storage.png
|   |   |   |   |           |   |-- structured_output
|   |   |   |   |           |   |   |-- diagram1.png
|   |   |   |   |           |   |   \-- program2.png
|   |   |   |   |           |   |-- vector_stores
|   |   |   |   |           |   |   |-- faiss_index_0.png
|   |   |   |   |           |   |   |-- faiss_index_1.png
|   |   |   |   |           |   |   |-- pinecone_index_0.png
|   |   |   |   |           |   |   |-- pinecone_reader.png
|   |   |   |   |           |   |   |-- qdrant_index_0.png
|   |   |   |   |           |   |   |-- qdrant_reader.png
|   |   |   |   |           |   |   |-- simple_index_0.png
|   |   |   |   |           |   |   |-- weaviate_index_0.png
|   |   |   |   |           |   |   |-- weaviate_reader_0.png
|   |   |   |   |           |   |   \-- weaviate_reader_1.png
|   |   |   |   |           |   \-- sitemap.xml
|   |   |   |   |           |-- changes
|   |   |   |   |           |   |-- _meta.yml
|   |   |   |   |           |   \-- deprecated_terms.md
|   |   |   |   |           |-- community
|   |   |   |   |           |   |-- faq
|   |   |   |   |           |   |   |-- _meta.yml
|   |   |   |   |           |   |   |-- chat_engines.md
|   |   |   |   |           |   |   |-- documents_and_nodes.md
|   |   |   |   |           |   |   |-- embeddings.md
|   |   |   |   |           |   |   |-- index.md
|   |   |   |   |           |   |   |-- llms.md
|   |   |   |   |           |   |   |-- query_engines.md
|   |   |   |   |           |   |   \-- vector_database.md
|   |   |   |   |           |   |-- integrations
|   |   |   |   |           |   |   |-- _meta.yml
|   |   |   |   |           |   |   |-- chatgpt_plugins.md
|   |   |   |   |           |   |   |-- deepeval.md
|   |   |   |   |           |   |   |-- fleet_libraries_context.md
|   |   |   |   |           |   |   |-- graph_stores.md
|   |   |   |   |           |   |   |-- graphsignal.md
|   |   |   |   |           |   |   |-- guidance.md
|   |   |   |   |           |   |   |-- lmformatenforcer.md
|   |   |   |   |           |   |   |-- managed_indices.md
|   |   |   |   |           |   |   |-- tonicvalidate.md
|   |   |   |   |           |   |   |-- trulens.md
|   |   |   |   |           |   |   |-- uptrain.md
|   |   |   |   |           |   |   \-- vector_stores.md
|   |   |   |   |           |   |-- llama_packs
|   |   |   |   |           |   |   |-- _meta.yml
|   |   |   |   |           |   |   \-- index.md
|   |   |   |   |           |   |-- _meta.yml
|   |   |   |   |           |   |-- full_stack_projects.md
|   |   |   |   |           |   \-- integrations.md
|   |   |   |   |           |-- css
|   |   |   |   |           |   |-- _meta.yml
|   |   |   |   |           |   |-- algolia.css
|   |   |   |   |           |   |-- custom.css
|   |   |   |   |           |   \-- style.css
|   |   |   |   |           |-- getting_started
|   |   |   |   |           |   |-- starter_tools
|   |   |   |   |           |   |   |-- _meta.yml
|   |   |   |   |           |   |   |-- chatllamaindex.png
|   |   |   |   |           |   |   |-- index.md
|   |   |   |   |           |   |   |-- llamabot.png
|   |   |   |   |           |   |   |-- rag_cli.md
|   |   |   |   |           |   |   \-- secinsights.png
|   |   |   |   |           |   |-- _meta.yml
|   |   |   |   |           |   |-- async_python.md
|   |   |   |   |           |   |-- basic_rag.png
|   |   |   |   |           |   |-- concepts.mdx
|   |   |   |   |           |   |-- discover_llamaindex.md
|   |   |   |   |           |   |-- faq.mdx
|   |   |   |   |           |   |-- indexing.jpg
|   |   |   |   |           |   |-- installation.mdx
|   |   |   |   |           |   |-- querying.jpg
|   |   |   |   |           |   |-- rag.jpg
|   |   |   |   |           |   |-- reading.md
|   |   |   |   |           |   |-- stages.png
|   |   |   |   |           |   |-- starter_example.mdx
|   |   |   |   |           |   \-- starter_example_local.mdx
|   |   |   |   |           |-- javascript
|   |   |   |   |           |   |-- _meta.yml
|   |   |   |   |           |   |-- algolia.js
|   |   |   |   |           |   |-- llms_example.js
|   |   |   |   |           |   \-- runllm.js
|   |   |   |   |           |-- llama_cloud
|   |   |   |   |           |   |-- _meta.yml
|   |   |   |   |           |   |-- index.md
|   |   |   |   |           |   \-- llama_parse.md
|   |   |   |   |           |-- module_guides
|   |   |   |   |           |   |-- deploying
|   |   |   |   |           |   |   |-- agents
|   |   |   |   |           |   |   |   |-- _meta.yml
|   |   |   |   |           |   |   |   |-- index.mdx
|   |   |   |   |           |   |   |   |-- memory.mdx
|   |   |   |   |           |   |   |   |-- modules.md
|   |   |   |   |           |   |   |   \-- tools.md
|   |   |   |   |           |   |   |-- chat_engines
|   |   |   |   |           |   |   |   |-- _meta.yml
|   |   |   |   |           |   |   |   |-- index.mdx
|   |   |   |   |           |   |   |   |-- modules.md
|   |   |   |   |           |   |   |   \-- usage_pattern.mdx
|   |   |   |   |           |   |   |-- query_engine
|   |   |   |   |           |   |   |   |-- _meta.yml
|   |   |   |   |           |   |   |   |-- index.mdx
|   |   |   |   |           |   |   |   |-- modules.md
|   |   |   |   |           |   |   |   |-- response_modes.md
|   |   |   |   |           |   |   |   |-- streaming.md
|   |   |   |   |           |   |   |   |-- supporting_modules.md
|   |   |   |   |           |   |   |   \-- usage_pattern.mdx
|   |   |   |   |           |   |   \-- _meta.yml
|   |   |   |   |           |   |-- evaluating
|   |   |   |   |           |   |   |-- _meta.yml
|   |   |   |   |           |   |   |-- contributing_llamadatasets.md
|   |   |   |   |           |   |   |-- evaluating_evaluators_with_llamadatasets.md
|   |   |   |   |           |   |   |-- evaluating_with_llamadatasets.md
|   |   |   |   |           |   |   |-- index.md
|   |   |   |   |           |   |   |-- modules.md
|   |   |   |   |           |   |   |-- usage_pattern.md
|   |   |   |   |           |   |   \-- usage_pattern_retrieval.md
|   |   |   |   |           |   |-- indexing
|   |   |   |   |           |   |   |-- _meta.yml
|   |   |   |   |           |   |   |-- document_management.md
|   |   |   |   |           |   |   |-- index.md
|   |   |   |   |           |   |   |-- index_guide.md
|   |   |   |   |           |   |   |-- llama_cloud_index.md
|   |   |   |   |           |   |   |-- lpg_index_guide.md
|   |   |   |   |           |   |   |-- metadata_extraction.md
|   |   |   |   |           |   |   |-- modules.md
|   |   |   |   |           |   |   |-- vector_store_guide.ipynb
|   |   |   |   |           |   |   \-- vector_store_index.mdx
|   |   |   |   |           |   |-- llama_deploy
|   |   |   |   |           |   |   |-- _meta.yml
|   |   |   |   |           |   |   \-- README.txt
|   |   |   |   |           |   |-- loading
|   |   |   |   |           |   |   |-- connector
|   |   |   |   |           |   |   |   |-- _meta.yml
|   |   |   |   |           |   |   |   |-- index.mdx
|   |   |   |   |           |   |   |   |-- llama_parse.md
|   |   |   |   |           |   |   |   |-- modules.md
|   |   |   |   |           |   |   |   \-- usage_pattern.md
|   |   |   |   |           |   |   |-- documents_and_nodes
|   |   |   |   |           |   |   |   |-- _meta.yml
|   |   |   |   |           |   |   |   |-- index.md
|   |   |   |   |           |   |   |   |-- usage_documents.md
|   |   |   |   |           |   |   |   |-- usage_metadata_extractor.md
|   |   |   |   |           |   |   |   \-- usage_nodes.md
|   |   |   |   |           |   |   |-- ingestion_pipeline
|   |   |   |   |           |   |   |   |-- _meta.yml
|   |   |   |   |           |   |   |   |-- index.md
|   |   |   |   |           |   |   |   \-- transformations.md
|   |   |   |   |           |   |   |-- node_parsers
|   |   |   |   |           |   |   |   |-- _meta.yml
|   |   |   |   |           |   |   |   |-- index.md
|   |   |   |   |           |   |   |   \-- modules.md
|   |   |   |   |           |   |   |-- _meta.yml
|   |   |   |   |           |   |   |-- index.md
|   |   |   |   |           |   |   \-- simpledirectoryreader.md
|   |   |   |   |           |   |-- mcp
|   |   |   |   |           |   |   |-- _meta.yml
|   |   |   |   |           |   |   |-- convert_existing.md
|   |   |   |   |           |   |   |-- index.md
|   |   |   |   |           |   |   |-- llamacloud_mcp.md
|   |   |   |   |           |   |   \-- llamaindex_mcp.md
|   |   |   |   |           |   |-- models
|   |   |   |   |           |   |   |-- llms
|   |   |   |   |           |   |   |   |-- _meta.yml
|   |   |   |   |           |   |   |   |-- local.md
|   |   |   |   |           |   |   |   |-- modules.md
|   |   |   |   |           |   |   |   |-- usage_custom.md
|   |   |   |   |           |   |   |   \-- usage_standalone.md
|   |   |   |   |           |   |   |-- prompts
|   |   |   |   |           |   |   |   |-- _meta.yml
|   |   |   |   |           |   |   |   |-- index.md
|   |   |   |   |           |   |   |   \-- usage_pattern.md
|   |   |   |   |           |   |   |-- _meta.yml
|   |   |   |   |           |   |   |-- embeddings.md
|   |   |   |   |           |   |   |-- index.md
|   |   |   |   |           |   |   |-- llms.md
|   |   |   |   |           |   |   \-- multi_modal.md
|   |   |   |   |           |   |-- observability
|   |   |   |   |           |   |   |-- callbacks
|   |   |   |   |           |   |   |   |-- _meta.yml
|   |   |   |   |           |   |   |   |-- index.md
|   |   |   |   |           |   |   |   \-- token_counting_migration.md
|   |   |   |   |           |   |   |-- _meta.yml
|   |   |   |   |           |   |   |-- index.md
|   |   |   |   |           |   |   \-- instrumentation.md
|   |   |   |   |           |   |-- querying
|   |   |   |   |           |   |   |-- node_postprocessors
|   |   |   |   |           |   |   |   |-- _meta.yml
|   |   |   |   |           |   |   |   |-- index.mdx
|   |   |   |   |           |   |   |   \-- node_postprocessors.md
|   |   |   |   |           |   |   |-- response_synthesizers
|   |   |   |   |           |   |   |   |-- _meta.yml
|   |   |   |   |           |   |   |   |-- index.mdx
|   |   |   |   |           |   |   |   \-- response_synthesizers.md
|   |   |   |   |           |   |   |-- retriever
|   |   |   |   |           |   |   |   |-- _meta.yml
|   |   |   |   |           |   |   |   |-- index.mdx
|   |   |   |   |           |   |   |   |-- retriever_modes.md
|   |   |   |   |           |   |   |   \-- retrievers.md
|   |   |   |   |           |   |   |-- router
|   |   |   |   |           |   |   |   |-- _meta.yml
|   |   |   |   |           |   |   |   \-- index.md
|   |   |   |   |           |   |   |-- structured_outputs
|   |   |   |   |           |   |   |   |-- _meta.yml
|   |   |   |   |           |   |   |   |-- index.md
|   |   |   |   |           |   |   |   |-- output_parser.md
|   |   |   |   |           |   |   |   |-- pydantic_program.mdx
|   |   |   |   |           |   |   |   \-- query_engine.mdx
|   |   |   |   |           |   |   |-- _meta.yml
|   |   |   |   |           |   |   \-- index.md
|   |   |   |   |           |   |-- storing
|   |   |   |   |           |   |   |-- _meta.yml
|   |   |   |   |           |   |   |-- chat_stores.md
|   |   |   |   |           |   |   |-- customization.md
|   |   |   |   |           |   |   |-- docstores.md
|   |   |   |   |           |   |   |-- index.md
|   |   |   |   |           |   |   |-- index_stores.md
|   |   |   |   |           |   |   |-- kv_stores.md
|   |   |   |   |           |   |   |-- save_load.md
|   |   |   |   |           |   |   \-- vector_stores.md
|   |   |   |   |           |   |-- supporting_modules
|   |   |   |   |           |   |   |-- _meta.yml
|   |   |   |   |           |   |   |-- service_context_migration.md
|   |   |   |   |           |   |   |-- settings.mdx
|   |   |   |   |           |   |   \-- supporting_modules.md
|   |   |   |   |           |   |-- _meta.yml
|   |   |   |   |           |   \-- index.md
|   |   |   |   |           |-- optimizing
|   |   |   |   |           |   |-- advanced_retrieval
|   |   |   |   |           |   |   |-- _meta.yml
|   |   |   |   |           |   |   |-- advanced_retrieval.md
|   |   |   |   |           |   |   \-- query_transformations.md
|   |   |   |   |           |   |-- agentic_strategies
|   |   |   |   |           |   |   |-- _meta.yml
|   |   |   |   |           |   |   \-- agentic_strategies.md
|   |   |   |   |           |   |-- basic_strategies
|   |   |   |   |           |   |   |-- _meta.yml
|   |   |   |   |           |   |   \-- basic_strategies.md
|   |   |   |   |           |   |-- evaluation
|   |   |   |   |           |   |   |-- _meta.yml
|   |   |   |   |           |   |   |-- component_wise_evaluation.md
|   |   |   |   |           |   |   |-- e2e_evaluation.md
|   |   |   |   |           |   |   \-- evaluation.md
|   |   |   |   |           |   |-- fine-tuning
|   |   |   |   |           |   |   |-- _meta.yml
|   |   |   |   |           |   |   \-- fine-tuning.md
|   |   |   |   |           |   |-- _meta.yml
|   |   |   |   |           |   |-- building_rag_from_scratch.md
|   |   |   |   |           |   |-- custom_modules.md
|   |   |   |   |           |   |-- production_rag.md
|   |   |   |   |           |   \-- rag_failure_mode_checklist.md
|   |   |   |   |           |-- presentations
|   |   |   |   |           |   |-- materials
|   |   |   |   |           |   |   |-- 2024-02-28-rag-bootcamp-vector-institute.ipynb
|   |   |   |   |           |   |   |-- 2024-04-02-otpp.ipynb
|   |   |   |   |           |   |   |-- 2024-04-04-vector-pe-lab.ipynb
|   |   |   |   |           |   |   |-- 2024-05-10-rbc-llm-workshop.ipynb
|   |   |   |   |           |   |   |-- 2024-06-13-vector-ess-oss-tools.ipynb
|   |   |   |   |           |   |   |-- 2024-06-19-georgian-genai-bootcamp.ipynb
|   |   |   |   |           |   |   |-- 2024-06-22-genai-philippines.ipynb
|   |   |   |   |           |   |   \-- _meta.yml
|   |   |   |   |           |   |-- _meta.yml
|   |   |   |   |           |   \-- past_presentations.md
|   |   |   |   |           |-- understanding
|   |   |   |   |           |   |-- agent
|   |   |   |   |           |   |   |-- _meta.yml
|   |   |   |   |           |   |   |-- agent_flow.png
|   |   |   |   |           |   |   |-- agentworkflow.jpg
|   |   |   |   |           |   |   |-- human_in_the_loop.md
|   |   |   |   |           |   |   |-- index.mdx
|   |   |   |   |           |   |   |-- multi_agent.md
|   |   |   |   |           |   |   |-- state.md
|   |   |   |   |           |   |   |-- streaming.mdx
|   |   |   |   |           |   |   |-- structured_output.md
|   |   |   |   |           |   |   \-- tools.md
|   |   |   |   |           |   |-- deployment
|   |   |   |   |           |   |   |-- _meta.yml
|   |   |   |   |           |   |   \-- deployment.md
|   |   |   |   |           |   |-- evaluating
|   |   |   |   |           |   |   |-- cost_analysis
|   |   |   |   |           |   |   |   |-- _meta.yml
|   |   |   |   |           |   |   |   |-- index.md
|   |   |   |   |           |   |   |   \-- usage_pattern.md
|   |   |   |   |           |   |   |-- _meta.yml
|   |   |   |   |           |   |   \-- evaluating.md
|   |   |   |   |           |   |-- extraction
|   |   |   |   |           |   |   |-- _meta.yml
|   |   |   |   |           |   |   |-- index.md
|   |   |   |   |           |   |   |-- lower_level.md
|   |   |   |   |           |   |   |-- structured_input.md
|   |   |   |   |           |   |   |-- structured_llms.md
|   |   |   |   |           |   |   \-- structured_prediction.md
|   |   |   |   |           |   |-- putting_it_all_together
|   |   |   |   |           |   |   |-- apps
|   |   |   |   |           |   |   |   |-- _meta.yml
|   |   |   |   |           |   |   |   |-- fullstack_app_guide.md
|   |   |   |   |           |   |   |   |-- fullstack_with_delphic.md
|   |   |   |   |           |   |   |   \-- index.md
|   |   |   |   |           |   |   |-- chatbots
|   |   |   |   |           |   |   |   |-- _meta.yml
|   |   |   |   |           |   |   |   \-- building_a_chatbot.md
|   |   |   |   |           |   |   |-- q_and_a
|   |   |   |   |           |   |   |   |-- _meta.yml
|   |   |   |   |           |   |   |   |-- index.md
|   |   |   |   |           |   |   |   \-- terms_definitions_tutorial.md
|   |   |   |   |           |   |   |-- structured_data
|   |   |   |   |           |   |   |   |-- _meta.yml
|   |   |   |   |           |   |   |   \-- index.md
|   |   |   |   |           |   |   |-- _meta.yml
|   |   |   |   |           |   |   |-- agents.md
|   |   |   |   |           |   |   \-- index.md
|   |   |   |   |           |   |-- rag
|   |   |   |   |           |   |   |-- indexing
|   |   |   |   |           |   |   |   |-- _meta.yml
|   |   |   |   |           |   |   |   \-- index.mdx
|   |   |   |   |           |   |   |-- loading
|   |   |   |   |           |   |   |   |-- _meta.yml
|   |   |   |   |           |   |   |   |-- index.md
|   |   |   |   |           |   |   |   |-- llamacloud.md
|   |   |   |   |           |   |   |   \-- llamahub.md
|   |   |   |   |           |   |   |-- querying
|   |   |   |   |           |   |   |   |-- _meta.yml
|   |   |   |   |           |   |   |   \-- index.mdx
|   |   |   |   |           |   |   |-- storing
|   |   |   |   |           |   |   |   |-- _meta.yml
|   |   |   |   |           |   |   |   \-- index.mdx
|   |   |   |   |           |   |   |-- _meta.yml
|   |   |   |   |           |   |   \-- index.mdx
|   |   |   |   |           |   |-- tracing_and_debugging
|   |   |   |   |           |   |   |-- _meta.yml
|   |   |   |   |           |   |   \-- tracing_and_debugging.md
|   |   |   |   |           |   |-- _meta.yml
|   |   |   |   |           |   |-- index.mdx
|   |   |   |   |           |   |-- privacy.md
|   |   |   |   |           |   \-- using_llms.mdx
|   |   |   |   |           |-- use_cases
|   |   |   |   |           |   |-- _meta.yml
|   |   |   |   |           |   |-- agents.md
|   |   |   |   |           |   |-- chatbots.md
|   |   |   |   |           |   |-- extraction.md
|   |   |   |   |           |   |-- fine_tuning.md
|   |   |   |   |           |   |-- graph_querying.md
|   |   |   |   |           |   |-- index.md
|   |   |   |   |           |   |-- multimodal.md
|   |   |   |   |           |   |-- prompting.md
|   |   |   |   |           |   |-- q_and_a.md
|   |   |   |   |           |   |-- querying_csvs.md
|   |   |   |   |           |   |-- tables_charts.md
|   |   |   |   |           |   \-- text_to_sql.md
|   |   |   |   |           |-- workflows
|   |   |   |   |           |   |-- .gitkeep
|   |   |   |   |           |   \-- _meta.yml
|   |   |   |   |           |-- _meta.yml
|   |   |   |   |           |-- CHANGELOG.md
|   |   |   |   |           |-- CONTRIBUTING.md
|   |   |   |   |           |-- index.md
|   |   |   |   |           |-- llms.txt
|   |   |   |   |           \-- sitemap.xml
|   |   |   |   \-- content.config.ts
|   |   |   |-- .gitignore
|   |   |   |-- astro.config.mjs
|   |   |   |-- DOCS_README.md
|   |   |   |-- package-lock.json
|   |   |   |-- package.json
|   |   |   \-- tsconfig.json
|   |   |-- llama-datasets
|   |   |   |-- 10k
|   |   |   |   \-- uber_2021
|   |   |   |       |-- card.json
|   |   |   |       |-- llamaindex_baseline.py
|   |   |   |       \-- README.md
|   |   |   |-- blockchain_solana
|   |   |   |   |-- card.json
|   |   |   |   |-- llamaindex_baseline.py
|   |   |   |   \-- README.md
|   |   |   |-- braintrust_coda
|   |   |   |   |-- __init__.py
|   |   |   |   |-- card.json
|   |   |   |   |-- llamaindex_baseline.py
|   |   |   |   \-- README.md
|   |   |   |-- covidqa
|   |   |   |   |-- card.json
|   |   |   |   |-- llamaindex_baseline.py
|   |   |   |   \-- README.md
|   |   |   |-- docugami_kg_rag
|   |   |   |   \-- sec_10_q
|   |   |   |       |-- card.json
|   |   |   |       |-- llamaindex_baseline.py
|   |   |   |       \-- README.md
|   |   |   |-- eval_llm_survey_paper
|   |   |   |   |-- card.json
|   |   |   |   |-- llamaindex_baseline.py
|   |   |   |   \-- README.md
|   |   |   |-- history_of_alexnet
|   |   |   |   |-- card.json
|   |   |   |   |-- llamaindex_baseline.py
|   |   |   |   \-- README.md
|   |   |   |-- llama2_paper
|   |   |   |   |-- __init__.py
|   |   |   |   |-- card.json
|   |   |   |   |-- llamaindex_baseline.py
|   |   |   |   \-- README.md
|   |   |   |-- mini_covidqa
|   |   |   |   |-- card.json
|   |   |   |   |-- llamaindex_baseline.py
|   |   |   |   \-- README.md
|   |   |   |-- mini_esg_bench
|   |   |   |   |-- card.json
|   |   |   |   |-- llamaindex_baseline.py
|   |   |   |   \-- README.md
|   |   |   |-- mini_mt_bench_singlegrading
|   |   |   |   |-- baselines.py
|   |   |   |   |-- card.json
|   |   |   |   \-- README.md
|   |   |   |-- mini_squadv2
|   |   |   |   |-- card.json
|   |   |   |   |-- llamaindex_baseline.py
|   |   |   |   \-- README.md
|   |   |   |-- mini_truthfulqa
|   |   |   |   |-- card.json
|   |   |   |   |-- llamaindex_baseline.py
|   |   |   |   \-- README.md
|   |   |   |-- mt_bench_humanjudgement
|   |   |   |   |-- baselines.py
|   |   |   |   |-- card.json
|   |   |   |   \-- README.md
|   |   |   |-- origin_of_covid19
|   |   |   |   |-- card.json
|   |   |   |   |-- llamaindex_baseline.py
|   |   |   |   \-- README.md
|   |   |   |-- patronus_financebench
|   |   |   |   |-- __init__.py
|   |   |   |   |-- card.json
|   |   |   |   |-- llamaindex_baseline.py
|   |   |   |   \-- README.md
|   |   |   |-- paul_graham_essay
|   |   |   |   |-- __init__.py
|   |   |   |   |-- card.json
|   |   |   |   |-- llamaindex_baseline.py
|   |   |   |   \-- README.md
|   |   |   |-- __init__.py
|   |   |   |-- library.json
|   |   |   \-- template_README.md
|   |   |-- llama-dev
|   |   |   |-- llama_dev
|   |   |   |   |-- pkg
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- bump.py
|   |   |   |   |   |-- cmd_exec.py
|   |   |   |   |   \-- info.py
|   |   |   |   |-- release
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- changelog.py
|   |   |   |   |   |-- check.py
|   |   |   |   |   \-- prepare.py
|   |   |   |   |-- test
|   |   |   |   |   \-- __init__.py
|   |   |   |   |-- __init__.py
|   |   |   |   |-- __main__.py
|   |   |   |   |-- cli.py
|   |   |   |   \-- utils.py
|   |   |   |-- tests
|   |   |   |   |-- data
|   |   |   |   |   |-- llama-index-integrations
|   |   |   |   |   |   |-- storage
|   |   |   |   |   |   |   \-- subcat
|   |   |   |   |   |   |       \-- pkg2
|   |   |   |   |   |   |           |-- tests
|   |   |   |   |   |   |           |   \-- .gitkeep
|   |   |   |   |   |   |           \-- pyproject.toml
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- pkg1
|   |   |   |   |   |   |       |-- tests
|   |   |   |   |   |   |       |   \-- .gitkeep
|   |   |   |   |   |   |       \-- pyproject.toml
|   |   |   |   |   |   \-- not_a_category
|   |   |   |   |   |-- llama-index-packs
|   |   |   |   |   |   |-- not_a_pack
|   |   |   |   |   |   |   \-- .gitkeep
|   |   |   |   |   |   |-- pack1
|   |   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |   \-- .gitkeep
|   |   |   |   |   |   |   \-- pyproject.toml
|   |   |   |   |   |   \-- pack2
|   |   |   |   |   |       \-- pyproject.toml
|   |   |   |   |   \-- llama-index-utils
|   |   |   |   |       |-- not_a_util
|   |   |   |   |       |   \-- .gitkeep
|   |   |   |   |       \-- util
|   |   |   |   |           |-- tests
|   |   |   |   |           |   \-- .gitkeep
|   |   |   |   |           \-- pyproject.toml
|   |   |   |   |-- pkg
|   |   |   |   |   |-- test_bump.py
|   |   |   |   |   |-- test_cmd_exec.py
|   |   |   |   |   \-- test_info.py
|   |   |   |   |-- release
|   |   |   |   |   |-- test_changelog.py
|   |   |   |   |   \-- test_check.py
|   |   |   |   |-- test
|   |   |   |   |   \-- test_test.py
|   |   |   |   |-- __init__.py
|   |   |   |   |-- conftest.py
|   |   |   |   |-- test_cli.py
|   |   |   |   \-- test_utils.py
|   |   |   |-- .gitignore
|   |   |   |-- LICENSE
|   |   |   |-- pyproject.toml
|   |   |   |-- README.md
|   |   |   \-- uv.lock
|   |   |-- llama-index-cli
|   |   |   |-- llama_index
|   |   |   |   \-- cli
|   |   |   |       |-- new_package
|   |   |   |       |   |-- common
|   |   |   |       |   |   |-- .gitignore
|   |   |   |       |   |   |-- _build
|   |   |   |       |   |   \-- Makefile
|   |   |   |       |   |-- templates
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- init.py
|   |   |   |       |   |   |-- pyproject.py
|   |   |   |       |   |   \-- readme.py
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   \-- base.py
|   |   |   |       |-- rag
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   \-- base.py
|   |   |   |       |-- upgrade
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- base.py
|   |   |   |       |   \-- mappings.json
|   |   |   |       |-- __init__.py
|   |   |   |       \-- command_line.py
|   |   |   |-- tests
|   |   |   |   |-- __init__.py
|   |   |   |   |-- test_cli.py
|   |   |   |   \-- test_rag.py
|   |   |   |-- .gitignore
|   |   |   |-- CHANGELOG.MD
|   |   |   |-- LICENSE
|   |   |   |-- Makefile
|   |   |   |-- pyproject.toml
|   |   |   \-- README.md
|   |   |-- llama-index-core
|   |   |   |-- llama_index
|   |   |   |   \-- core
|   |   |   |       |-- _static
|   |   |   |       |   |-- nltk_cache
|   |   |   |       |   |   \-- .gitignore
|   |   |   |       |   |-- tiktoken_cache
|   |   |   |       |   |   \-- .gitignore
|   |   |   |       |   \-- .gitignore
|   |   |   |       |-- agent
|   |   |   |       |   |-- react
|   |   |   |       |   |   |-- templates
|   |   |   |       |   |   |   \-- system_header_template.md
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- formatter.py
|   |   |   |       |   |   |-- output_parser.py
|   |   |   |       |   |   |-- prompts.py
|   |   |   |       |   |   \-- types.py
|   |   |   |       |   |-- workflow
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- agent_context.py
|   |   |   |       |   |   |-- base_agent.py
|   |   |   |       |   |   |-- codeact_agent.py
|   |   |   |       |   |   |-- function_agent.py
|   |   |   |       |   |   |-- multi_agent_workflow.py
|   |   |   |       |   |   |-- prompts.py
|   |   |   |       |   |   |-- react_agent.py
|   |   |   |       |   |   \-- workflow_events.py
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   \-- utils.py
|   |   |   |       |-- base
|   |   |   |       |   |-- embeddings
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- base.py
|   |   |   |       |   |   \-- base_sparse.py
|   |   |   |       |   |-- llms
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- base.py
|   |   |   |       |   |   |-- generic_utils.py
|   |   |   |       |   |   \-- types.py
|   |   |   |       |   |-- response
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   \-- schema.py
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- base_auto_retriever.py
|   |   |   |       |   |-- base_multi_modal_retriever.py
|   |   |   |       |   |-- base_query_engine.py
|   |   |   |       |   |-- base_retriever.py
|   |   |   |       |   \-- base_selector.py
|   |   |   |       |-- bridge
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- langchain.py
|   |   |   |       |   |-- pydantic.py
|   |   |   |       |   |-- pydantic_core.py
|   |   |   |       |   \-- pydantic_settings.py
|   |   |   |       |-- callbacks
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- base.py
|   |   |   |       |   |-- base_handler.py
|   |   |   |       |   |-- global_handlers.py
|   |   |   |       |   |-- llama_debug.py
|   |   |   |       |   |-- pythonically_printing_base_handler.py
|   |   |   |       |   |-- schema.py
|   |   |   |       |   |-- simple_llm_handler.py
|   |   |   |       |   |-- token_counting.py
|   |   |   |       |   \-- utils.py
|   |   |   |       |-- chat_engine
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- condense_plus_context.py
|   |   |   |       |   |-- condense_question.py
|   |   |   |       |   |-- context.py
|   |   |   |       |   |-- multi_modal_condense_plus_context.py
|   |   |   |       |   |-- multi_modal_context.py
|   |   |   |       |   |-- simple.py
|   |   |   |       |   |-- types.py
|   |   |   |       |   \-- utils.py
|   |   |   |       |-- chat_ui
|   |   |   |       |   |-- models
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   \-- artifact.py
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   \-- events.py
|   |   |   |       |-- command_line
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- mappings.json
|   |   |   |       |   \-- upgrade.py
|   |   |   |       |-- composability
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- base.py
|   |   |   |       |   \-- joint_qa_summary.py
|   |   |   |       |-- data_structs
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- data_structs.py
|   |   |   |       |   |-- document_summary.py
|   |   |   |       |   |-- registry.py
|   |   |   |       |   |-- struct_type.py
|   |   |   |       |   \-- table.py
|   |   |   |       |-- download
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- dataset.py
|   |   |   |       |   |-- integration.py
|   |   |   |       |   |-- module.py
|   |   |   |       |   |-- pack.py
|   |   |   |       |   \-- utils.py
|   |   |   |       |-- embeddings
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- loading.py
|   |   |   |       |   |-- mock_embed_model.py
|   |   |   |       |   |-- multi_modal_base.py
|   |   |   |       |   |-- pooling.py
|   |   |   |       |   \-- utils.py
|   |   |   |       |-- evaluation
|   |   |   |       |   |-- benchmarks
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- beir.py
|   |   |   |       |   |   \-- hotpotqa.py
|   |   |   |       |   |-- multi_modal
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- faithfulness.py
|   |   |   |       |   |   \-- relevancy.py
|   |   |   |       |   |-- retrieval
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- base.py
|   |   |   |       |   |   |-- evaluator.py
|   |   |   |       |   |   |-- metrics.py
|   |   |   |       |   |   \-- metrics_base.py
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- answer_relevancy.py
|   |   |   |       |   |-- base.py
|   |   |   |       |   |-- batch_runner.py
|   |   |   |       |   |-- context_relevancy.py
|   |   |   |       |   |-- correctness.py
|   |   |   |       |   |-- dataset_generation.py
|   |   |   |       |   |-- eval_utils.py
|   |   |   |       |   |-- faithfulness.py
|   |   |   |       |   |-- guideline.py
|   |   |   |       |   |-- notebook_utils.py
|   |   |   |       |   |-- pairwise.py
|   |   |   |       |   |-- relevancy.py
|   |   |   |       |   \-- semantic_similarity.py
|   |   |   |       |-- extractors
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- document_context.py
|   |   |   |       |   |-- interface.py
|   |   |   |       |   |-- loading.py
|   |   |   |       |   \-- metadata_extractors.py
|   |   |   |       |-- graph_stores
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- prompts.py
|   |   |   |       |   |-- simple.py
|   |   |   |       |   |-- simple_labelled.py
|   |   |   |       |   |-- types.py
|   |   |   |       |   \-- utils.py
|   |   |   |       |-- indices
|   |   |   |       |   |-- common
|   |   |   |       |   |   |-- struct_store
|   |   |   |       |   |   |   |-- __init__.py
|   |   |   |       |   |   |   |-- base.py
|   |   |   |       |   |   |   |-- schema.py
|   |   |   |       |   |   |   \-- sql.py
|   |   |   |       |   |   \-- __init__.py
|   |   |   |       |   |-- common_tree
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   \-- base.py
|   |   |   |       |   |-- composability
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   \-- graph.py
|   |   |   |       |   |-- document_summary
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- base.py
|   |   |   |       |   |   \-- retrievers.py
|   |   |   |       |   |-- empty
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- base.py
|   |   |   |       |   |   \-- retrievers.py
|   |   |   |       |   |-- keyword_table
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- base.py
|   |   |   |       |   |   |-- rake_base.py
|   |   |   |       |   |   |-- README.md
|   |   |   |       |   |   |-- retrievers.py
|   |   |   |       |   |   |-- simple_base.py
|   |   |   |       |   |   \-- utils.py
|   |   |   |       |   |-- knowledge_graph
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- base.py
|   |   |   |       |   |   \-- retrievers.py
|   |   |   |       |   |-- list
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- base.py
|   |   |   |       |   |   |-- README.md
|   |   |   |       |   |   \-- retrievers.py
|   |   |   |       |   |-- managed
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- base.py
|   |   |   |       |   |   \-- types.py
|   |   |   |       |   |-- multi_modal
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- base.py
|   |   |   |       |   |   \-- retriever.py
|   |   |   |       |   |-- property_graph
|   |   |   |       |   |   |-- sub_retrievers
|   |   |   |       |   |   |   |-- __init__.py
|   |   |   |       |   |   |   |-- base.py
|   |   |   |       |   |   |   |-- custom.py
|   |   |   |       |   |   |   |-- cypher_template.py
|   |   |   |       |   |   |   |-- llm_synonym.py
|   |   |   |       |   |   |   |-- text_to_cypher.py
|   |   |   |       |   |   |   \-- vector.py
|   |   |   |       |   |   |-- transformations
|   |   |   |       |   |   |   |-- __init__.py
|   |   |   |       |   |   |   |-- dynamic_llm.py
|   |   |   |       |   |   |   |-- implicit.py
|   |   |   |       |   |   |   |-- schema_llm.py
|   |   |   |       |   |   |   |-- simple_llm.py
|   |   |   |       |   |   |   \-- utils.py
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- base.py
|   |   |   |       |   |   |-- retriever.py
|   |   |   |       |   |   \-- utils.py
|   |   |   |       |   |-- query
|   |   |   |       |   |   |-- query_transform
|   |   |   |       |   |   |   |-- __init__.py
|   |   |   |       |   |   |   |-- base.py
|   |   |   |       |   |   |   |-- feedback_transform.py
|   |   |   |       |   |   |   \-- prompts.py
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- base.py
|   |   |   |       |   |   |-- embedding_utils.py
|   |   |   |       |   |   \-- schema.py
|   |   |   |       |   |-- struct_store
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- base.py
|   |   |   |       |   |   |-- container_builder.py
|   |   |   |       |   |   |-- json_query.py
|   |   |   |       |   |   |-- pandas.py
|   |   |   |       |   |   |-- sql.py
|   |   |   |       |   |   |-- sql_query.py
|   |   |   |       |   |   \-- sql_retriever.py
|   |   |   |       |   |-- tree
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- all_leaf_retriever.py
|   |   |   |       |   |   |-- base.py
|   |   |   |       |   |   |-- inserter.py
|   |   |   |       |   |   |-- README.md
|   |   |   |       |   |   |-- select_leaf_embedding_retriever.py
|   |   |   |       |   |   |-- select_leaf_retriever.py
|   |   |   |       |   |   |-- tree_root_retriever.py
|   |   |   |       |   |   \-- utils.py
|   |   |   |       |   |-- vector_store
|   |   |   |       |   |   |-- retrievers
|   |   |   |       |   |   |   |-- auto_retriever
|   |   |   |       |   |   |   |   |-- __init__.py
|   |   |   |       |   |   |   |   |-- auto_retriever.py
|   |   |   |       |   |   |   |   |-- output_parser.py
|   |   |   |       |   |   |   |   \-- prompts.py
|   |   |   |       |   |   |   |-- __init__.py
|   |   |   |       |   |   |   \-- retriever.py
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   \-- base.py
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- base.py
|   |   |   |       |   |-- base_retriever.py
|   |   |   |       |   |-- loading.py
|   |   |   |       |   |-- postprocessor.py
|   |   |   |       |   |-- prompt_helper.py
|   |   |   |       |   |-- registry.py
|   |   |   |       |   \-- utils.py
|   |   |   |       |-- ingestion
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- api_utils.py
|   |   |   |       |   |-- cache.py
|   |   |   |       |   |-- data_sinks.py
|   |   |   |       |   |-- data_sources.py
|   |   |   |       |   |-- pipeline.py
|   |   |   |       |   \-- transformations.py
|   |   |   |       |-- instrumentation
|   |   |   |       |   |-- event_handlers
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- base.py
|   |   |   |       |   |   \-- null.py
|   |   |   |       |   |-- events
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- agent.py
|   |   |   |       |   |   |-- base.py
|   |   |   |       |   |   |-- chat_engine.py
|   |   |   |       |   |   |-- embedding.py
|   |   |   |       |   |   |-- exception.py
|   |   |   |       |   |   |-- llm.py
|   |   |   |       |   |   |-- query.py
|   |   |   |       |   |   |-- rerank.py
|   |   |   |       |   |   |-- retrieval.py
|   |   |   |       |   |   |-- span.py
|   |   |   |       |   |   \-- synthesis.py
|   |   |   |       |   |-- span
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- base.py
|   |   |   |       |   |   \-- simple.py
|   |   |   |       |   |-- span_handlers
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- base.py
|   |   |   |       |   |   |-- null.py
|   |   |   |       |   |   \-- simple.py
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- base_handler.py
|   |   |   |       |   \-- dispatcher.py
|   |   |   |       |-- langchain_helpers
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- streaming.py
|   |   |   |       |   \-- text_splitter.py
|   |   |   |       |-- llama_dataset
|   |   |   |       |   |-- legacy
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   \-- embedding.py
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- base.py
|   |   |   |       |   |-- download.py
|   |   |   |       |   |-- evaluator_evaluation.py
|   |   |   |       |   |-- generator.py
|   |   |   |       |   |-- rag.py
|   |   |   |       |   \-- simple.py
|   |   |   |       |-- llama_pack
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- base.py
|   |   |   |       |   \-- download.py
|   |   |   |       |-- llms
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- callbacks.py
|   |   |   |       |   |-- chatml_utils.py
|   |   |   |       |   |-- custom.py
|   |   |   |       |   |-- function_calling.py
|   |   |   |       |   |-- llm.py
|   |   |   |       |   |-- loading.py
|   |   |   |       |   |-- mock.py
|   |   |   |       |   |-- structured_llm.py
|   |   |   |       |   \-- utils.py
|   |   |   |       |-- memory
|   |   |   |       |   |-- memory_blocks
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- fact.py
|   |   |   |       |   |   |-- static.py
|   |   |   |       |   |   \-- vector.py
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- chat_memory_buffer.py
|   |   |   |       |   |-- chat_summary_memory_buffer.py
|   |   |   |       |   |-- memory.py
|   |   |   |       |   |-- simple_composable_memory.py
|   |   |   |       |   |-- types.py
|   |   |   |       |   \-- vector_memory.py
|   |   |   |       |-- multi_modal_llms
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- base.py
|   |   |   |       |   \-- generic_utils.py
|   |   |   |       |-- node_parser
|   |   |   |       |   |-- file
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- html.py
|   |   |   |       |   |   |-- json.py
|   |   |   |       |   |   |-- markdown.py
|   |   |   |       |   |   \-- simple_file.py
|   |   |   |       |   |-- relational
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- base_element.py
|   |   |   |       |   |   |-- hierarchical.py
|   |   |   |       |   |   |-- llama_parse_json_element.py
|   |   |   |       |   |   |-- markdown_element.py
|   |   |   |       |   |   |-- unstructured_element.py
|   |   |   |       |   |   \-- utils.py
|   |   |   |       |   |-- text
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- code.py
|   |   |   |       |   |   |-- langchain.py
|   |   |   |       |   |   |-- semantic_double_merging_splitter.py
|   |   |   |       |   |   |-- semantic_splitter.py
|   |   |   |       |   |   |-- sentence.py
|   |   |   |       |   |   |-- sentence_window.py
|   |   |   |       |   |   |-- token.py
|   |   |   |       |   |   \-- utils.py
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- interface.py
|   |   |   |       |   |-- loading.py
|   |   |   |       |   \-- node_utils.py
|   |   |   |       |-- objects
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- base.py
|   |   |   |       |   |-- base_node_mapping.py
|   |   |   |       |   |-- fn_node_mapping.py
|   |   |   |       |   |-- table_node_mapping.py
|   |   |   |       |   |-- tool_node_mapping.py
|   |   |   |       |   \-- utils.py
|   |   |   |       |-- output_parsers
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- base.py
|   |   |   |       |   |-- pydantic.py
|   |   |   |       |   |-- selection.py
|   |   |   |       |   \-- utils.py
|   |   |   |       |-- playground
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   \-- base.py
|   |   |   |       |-- postprocessor
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- llm_rerank.py
|   |   |   |       |   |-- metadata_replacement.py
|   |   |   |       |   |-- node.py
|   |   |   |       |   |-- node_recency.py
|   |   |   |       |   |-- optimizer.py
|   |   |   |       |   |-- pii.py
|   |   |   |       |   |-- rankGPT_rerank.py
|   |   |   |       |   |-- sbert_rerank.py
|   |   |   |       |   |-- structured_llm_rerank.py
|   |   |   |       |   \-- types.py
|   |   |   |       |-- program
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- function_program.py
|   |   |   |       |   |-- llm_program.py
|   |   |   |       |   |-- llm_prompt_program.py
|   |   |   |       |   |-- multi_modal_llm_program.py
|   |   |   |       |   |-- streaming_utils.py
|   |   |   |       |   \-- utils.py
|   |   |   |       |-- prompts
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- base.py
|   |   |   |       |   |-- chat_prompts.py
|   |   |   |       |   |-- default_prompt_selectors.py
|   |   |   |       |   |-- default_prompts.py
|   |   |   |       |   |-- display_utils.py
|   |   |   |       |   |-- guidance_utils.py
|   |   |   |       |   |-- mixin.py
|   |   |   |       |   |-- prompt_type.py
|   |   |   |       |   |-- prompt_utils.py
|   |   |   |       |   |-- prompts.py
|   |   |   |       |   |-- rich.py
|   |   |   |       |   |-- system.py
|   |   |   |       |   \-- utils.py
|   |   |   |       |-- query_engine
|   |   |   |       |   |-- flare
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- answer_inserter.py
|   |   |   |       |   |   |-- base.py
|   |   |   |       |   |   |-- output_parser.py
|   |   |   |       |   |   \-- schema.py
|   |   |   |       |   |-- jsonalyze
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   \-- jsonalyze_query_engine.py
|   |   |   |       |   |-- pandas
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- output_parser.py
|   |   |   |       |   |   \-- pandas_query_engine.py
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- citation_query_engine.py
|   |   |   |       |   |-- cogniswitch_query_engine.py
|   |   |   |       |   |-- custom.py
|   |   |   |       |   |-- graph_query_engine.py
|   |   |   |       |   |-- knowledge_graph_query_engine.py
|   |   |   |       |   |-- multi_modal.py
|   |   |   |       |   |-- multistep_query_engine.py
|   |   |   |       |   |-- retriever_query_engine.py
|   |   |   |       |   |-- retry_query_engine.py
|   |   |   |       |   |-- retry_source_query_engine.py
|   |   |   |       |   |-- router_query_engine.py
|   |   |   |       |   |-- sql_join_query_engine.py
|   |   |   |       |   |-- sql_vector_query_engine.py
|   |   |   |       |   |-- sub_question_query_engine.py
|   |   |   |       |   \-- transform_query_engine.py
|   |   |   |       |-- question_gen
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- llm_generators.py
|   |   |   |       |   |-- output_parser.py
|   |   |   |       |   |-- prompts.py
|   |   |   |       |   \-- types.py
|   |   |   |       |-- readers
|   |   |   |       |   |-- file
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   \-- base.py
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- base.py
|   |   |   |       |   |-- download.py
|   |   |   |       |   |-- json.py
|   |   |   |       |   |-- loading.py
|   |   |   |       |   \-- string_iterable.py
|   |   |   |       |-- response
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- notebook_utils.py
|   |   |   |       |   |-- pprint_utils.py
|   |   |   |       |   \-- utils.py
|   |   |   |       |-- response_synthesizers
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- accumulate.py
|   |   |   |       |   |-- base.py
|   |   |   |       |   |-- compact_and_accumulate.py
|   |   |   |       |   |-- compact_and_refine.py
|   |   |   |       |   |-- context_only.py
|   |   |   |       |   |-- factory.py
|   |   |   |       |   |-- generation.py
|   |   |   |       |   |-- no_text.py
|   |   |   |       |   |-- refine.py
|   |   |   |       |   |-- simple_summarize.py
|   |   |   |       |   |-- tree_summarize.py
|   |   |   |       |   \-- type.py
|   |   |   |       |-- retrievers
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- auto_merging_retriever.py
|   |   |   |       |   |-- fusion_retriever.py
|   |   |   |       |   |-- recursive_retriever.py
|   |   |   |       |   |-- router_retriever.py
|   |   |   |       |   \-- transform_retriever.py
|   |   |   |       |-- selectors
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- embedding_selectors.py
|   |   |   |       |   |-- llm_selectors.py
|   |   |   |       |   |-- prompts.py
|   |   |   |       |   |-- pydantic_selectors.py
|   |   |   |       |   \-- utils.py
|   |   |   |       |-- service_context_elements
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- llama_logger.py
|   |   |   |       |   \-- llm_predictor.py
|   |   |   |       |-- sparse_embeddings
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   \-- mock_sparse_embedding.py
|   |   |   |       |-- storage
|   |   |   |       |   |-- chat_store
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- base.py
|   |   |   |       |   |   |-- base_db.py
|   |   |   |       |   |   |-- loading.py
|   |   |   |       |   |   |-- simple_chat_store.py
|   |   |   |       |   |   \-- sql.py
|   |   |   |       |   |-- docstore
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- keyval_docstore.py
|   |   |   |       |   |   |-- registry.py
|   |   |   |       |   |   |-- simple_docstore.py
|   |   |   |       |   |   |-- types.py
|   |   |   |       |   |   \-- utils.py
|   |   |   |       |   |-- index_store
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- keyval_index_store.py
|   |   |   |       |   |   |-- simple_index_store.py
|   |   |   |       |   |   |-- types.py
|   |   |   |       |   |   \-- utils.py
|   |   |   |       |   |-- kvstore
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- simple_kvstore.py
|   |   |   |       |   |   \-- types.py
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   \-- storage_context.py
|   |   |   |       |-- text_splitter
|   |   |   |       |   \-- __init__.py
|   |   |   |       |-- tools
|   |   |   |       |   |-- tool_spec
|   |   |   |       |   |   |-- load_and_search
|   |   |   |       |   |   |   |-- __init__.py
|   |   |   |       |   |   |   |-- base.py
|   |   |   |       |   |   |   \-- README.md
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   \-- base.py
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- calling.py
|   |   |   |       |   |-- download.py
|   |   |   |       |   |-- eval_query_engine.py
|   |   |   |       |   |-- function_tool.py
|   |   |   |       |   |-- ondemand_loader_tool.py
|   |   |   |       |   |-- query_engine.py
|   |   |   |       |   |-- query_plan.py
|   |   |   |       |   |-- retriever_tool.py
|   |   |   |       |   |-- types.py
|   |   |   |       |   \-- utils.py
|   |   |   |       |-- utilities
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- aws_utils.py
|   |   |   |       |   |-- gemini_utils.py
|   |   |   |       |   |-- sql_wrapper.py
|   |   |   |       |   \-- token_counting.py
|   |   |   |       |-- vector_stores
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- simple.py
|   |   |   |       |   |-- types.py
|   |   |   |       |   \-- utils.py
|   |   |   |       |-- voice_agents
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- base.py
|   |   |   |       |   |-- events.py
|   |   |   |       |   |-- interface.py
|   |   |   |       |   \-- websocket.py
|   |   |   |       |-- workflow
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- context.py
|   |   |   |       |   |-- context_serializers.py
|   |   |   |       |   |-- decorators.py
|   |   |   |       |   |-- drawing.py
|   |   |   |       |   |-- errors.py
|   |   |   |       |   |-- events.py
|   |   |   |       |   |-- handler.py
|   |   |   |       |   |-- resource.py
|   |   |   |       |   |-- retry_policy.py
|   |   |   |       |   |-- service.py
|   |   |   |       |   |-- types.py
|   |   |   |       |   |-- utils.py
|   |   |   |       |   \-- workflow.py
|   |   |   |       |-- __init__.py
|   |   |   |       |-- async_utils.py
|   |   |   |       |-- constants.py
|   |   |   |       |-- image_retriever.py
|   |   |   |       |-- img_utils.py
|   |   |   |       |-- py.typed
|   |   |   |       |-- rate_limiter.py
|   |   |   |       |-- schema.py
|   |   |   |       |-- service_context.py
|   |   |   |       |-- settings.py
|   |   |   |       |-- types.py
|   |   |   |       \-- utils.py
|   |   |   |-- tests
|   |   |   |   |-- agent
|   |   |   |   |   |-- memory
|   |   |   |   |   |   |-- test_simple_composable.py
|   |   |   |   |   |   \-- test_vector_memory.py
|   |   |   |   |   |-- react
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_prompt_customization.py
|   |   |   |   |   |   |-- test_react_chat_formatter.py
|   |   |   |   |   |   \-- test_react_output_parser.py
|   |   |   |   |   |-- utils
|   |   |   |   |   |   \-- test_agent_utils.py
|   |   |   |   |   |-- workflow
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_agent_with_structured_output.py
|   |   |   |   |   |   |-- test_code_act_agent.py
|   |   |   |   |   |   |-- test_events.py
|   |   |   |   |   |   |-- test_function_call.py
|   |   |   |   |   |   |-- test_multi_agent_workflow.py
|   |   |   |   |   |   |-- test_react_agent.py
|   |   |   |   |   |   |-- test_return_direct_e2e.py
|   |   |   |   |   |   |-- test_single_agent_workflow.py
|   |   |   |   |   |   \-- test_thinking_delta.py
|   |   |   |   |   \-- __init__.py
|   |   |   |   |-- base
|   |   |   |   |   |-- llms
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_types.py
|   |   |   |   |   \-- __init__.py
|   |   |   |   |-- callbacks
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- test_llama_debug.py
|   |   |   |   |   |-- test_token_budget.py
|   |   |   |   |   \-- test_token_counter.py
|   |   |   |   |-- chat_engine
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- test_condense_plus_context.py
|   |   |   |   |   |-- test_condense_question.py
|   |   |   |   |   |-- test_context.py
|   |   |   |   |   |-- test_mm_condense_plus_context.py
|   |   |   |   |   |-- test_multi_modal_context.py
|   |   |   |   |   \-- test_simple.py
|   |   |   |   |-- embeddings
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- test_base.py
|   |   |   |   |   |-- test_utils.py
|   |   |   |   |   |-- test_with_cache.py
|   |   |   |   |   \-- todo_hf_test_utils.py
|   |   |   |   |-- evaluation
|   |   |   |   |   |-- test_base.py
|   |   |   |   |   |-- test_batch_runner.py
|   |   |   |   |   |-- test_dataset_generation.py
|   |   |   |   |   |-- test_metrics.py
|   |   |   |   |   \-- test_platform_eval.py
|   |   |   |   |-- extractors
|   |   |   |   |   |-- test_document_context_extractor.py
|   |   |   |   |   \-- test_extractor_resilience.py
|   |   |   |   |-- graph_stores
|   |   |   |   |   \-- test_simple_lpg.py
|   |   |   |   |-- indices
|   |   |   |   |   |-- document_summary
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_index.py
|   |   |   |   |   |   \-- test_retrievers.py
|   |   |   |   |   |-- empty
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_base.py
|   |   |   |   |   |-- keyword_table
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_base.py
|   |   |   |   |   |   |-- test_retrievers.py
|   |   |   |   |   |   \-- test_utils.py
|   |   |   |   |   |-- knowledge_graph
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_base.py
|   |   |   |   |   |   \-- test_retrievers.py
|   |   |   |   |   |-- list
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_index.py
|   |   |   |   |   |   \-- test_retrievers.py
|   |   |   |   |   |-- property_graph
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_property_graph.py
|   |   |   |   |   |   \-- test_schema_utils.py
|   |   |   |   |   |-- query
|   |   |   |   |   |   |-- query_transform
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- mock_utils.py
|   |   |   |   |   |   |   \-- test_base.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_compose.py
|   |   |   |   |   |   |-- test_compose_vector.py
|   |   |   |   |   |   |-- test_embedding_utils.py
|   |   |   |   |   |   \-- test_query_bundle.py
|   |   |   |   |   |-- response
|   |   |   |   |   |   |-- test_response_builder.py
|   |   |   |   |   |   \-- test_tree_summarize.py
|   |   |   |   |   |-- struct_store
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_base.py
|   |   |   |   |   |   |-- test_json_query.py
|   |   |   |   |   |   \-- test_sql_query.py
|   |   |   |   |   |-- tree
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_embedding_retriever.py
|   |   |   |   |   |   |-- test_index.py
|   |   |   |   |   |   \-- test_retrievers.py
|   |   |   |   |   |-- vector_store
|   |   |   |   |   |   |-- auto_retriever
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_output_parser.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- mock_services.py
|   |   |   |   |   |   |-- test_retrievers.py
|   |   |   |   |   |   |-- test_simple.py
|   |   |   |   |   |   \-- test_simple_async.py
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- conftest.py
|   |   |   |   |   |-- test_loading.py
|   |   |   |   |   |-- test_loading_graph.py
|   |   |   |   |   |-- test_prompt_helper.py
|   |   |   |   |   \-- test_utils.py
|   |   |   |   |-- ingestion
|   |   |   |   |   |-- test_cache.py
|   |   |   |   |   |-- test_data_sinks.py
|   |   |   |   |   |-- test_data_sources.py
|   |   |   |   |   |-- test_pipeline.py
|   |   |   |   |   \-- test_transformations.py
|   |   |   |   |-- llms
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- test_callbacks.py
|   |   |   |   |   |-- test_custom.py
|   |   |   |   |   |-- test_function_calling.py
|   |   |   |   |   |-- test_mock.py
|   |   |   |   |   \-- test_predict_and_call.py
|   |   |   |   |-- memory
|   |   |   |   |   |-- blocks
|   |   |   |   |   |   |-- test_fact.py
|   |   |   |   |   |   |-- test_static.py
|   |   |   |   |   |   \-- test_vector.py
|   |   |   |   |   |-- test_chat_memory_buffer.py
|   |   |   |   |   |-- test_chat_summary_memory_buffer.py
|   |   |   |   |   |-- test_memory_base.py
|   |   |   |   |   |-- test_memory_blocks_base.py
|   |   |   |   |   \-- test_memory_schema.py
|   |   |   |   |-- mock_utils
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- mock_predict.py
|   |   |   |   |   |-- mock_prompts.py
|   |   |   |   |   |-- mock_text_splitter.py
|   |   |   |   |   \-- mock_utils.py
|   |   |   |   |-- multi_modal_llms
|   |   |   |   |   |-- test_base_multi_modal_llm_metadata.py
|   |   |   |   |   \-- test_generic_utils.py
|   |   |   |   |-- node_parser
|   |   |   |   |   |-- metadata_extractor.py
|   |   |   |   |   |-- sentence_window.py
|   |   |   |   |   |-- test_duplicate_text_positions.py
|   |   |   |   |   |-- test_file.py
|   |   |   |   |   |-- test_hierarchical.py
|   |   |   |   |   |-- test_html.py
|   |   |   |   |   |-- test_json.py
|   |   |   |   |   |-- test_markdown.py
|   |   |   |   |   |-- test_markdown_element.py
|   |   |   |   |   |-- test_node_parser.py
|   |   |   |   |   |-- test_semantic_double_merging_splitter.py
|   |   |   |   |   |-- test_semantic_splitter.py
|   |   |   |   |   \-- test_unstructured.py
|   |   |   |   |-- objects
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- test_base.py
|   |   |   |   |   \-- test_node_mapping.py
|   |   |   |   |-- output_parsers
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- test_pydantic.py
|   |   |   |   |   |-- test_selection.py
|   |   |   |   |   \-- test_utils.py
|   |   |   |   |-- playground
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_base.py
|   |   |   |   |-- postprocessor
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- test_base.py
|   |   |   |   |   |-- test_llm_rerank.py
|   |   |   |   |   |-- test_metadata_replacement.py
|   |   |   |   |   |-- test_optimizer.py
|   |   |   |   |   |-- test_rankgpt_rerank.py
|   |   |   |   |   \-- test_structured_llm_rerank.py
|   |   |   |   |-- program
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- test_function_program.py
|   |   |   |   |   |-- test_llm_program.py
|   |   |   |   |   |-- test_multi_modal_llm_program.py
|   |   |   |   |   |-- test_streaming_utils.py
|   |   |   |   |   \-- test_utils.py
|   |   |   |   |-- prompts
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- test_base.py
|   |   |   |   |   |-- test_guidance_utils.py
|   |   |   |   |   |-- test_mixin.py
|   |   |   |   |   |-- test_rich.py
|   |   |   |   |   \-- test_utils.py
|   |   |   |   |-- query_engine
|   |   |   |   |   |-- test_cogniswitch_query_engine.py
|   |   |   |   |   |-- test_retriever_query_engine.py
|   |   |   |   |   \-- test_router_query_engine.py
|   |   |   |   |-- question_gen
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_llm_generators.py
|   |   |   |   |-- readers
|   |   |   |   |   |-- file
|   |   |   |   |   |   |-- data
|   |   |   |   |   |   |   |-- empty
|   |   |   |   |   |   |   |   \-- .gitkeep
|   |   |   |   |   |   |   |-- excluded
|   |   |   |   |   |   |   |   \-- excluded_1.txt
|   |   |   |   |   |   |   |-- sub
|   |   |   |   |   |   |   |   \-- file_1.txt
|   |   |   |   |   |   |   |-- excluded_0.txt
|   |   |   |   |   |   |   |-- file_0.md
|   |   |   |   |   |   |   \-- file_0.xyz
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_base.py
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- test_json.py
|   |   |   |   |   |-- test_load_reader.py
|   |   |   |   |   \-- test_string_iterable.py
|   |   |   |   |-- response_synthesizers
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- test_generate.py
|   |   |   |   |   \-- test_refine.py
|   |   |   |   |-- retrievers
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_composable_retriever.py
|   |   |   |   |-- schema
|   |   |   |   |   |-- data
|   |   |   |   |   |   \-- data.txt
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- test_base_component.py
|   |   |   |   |   |-- test_base_node.py
|   |   |   |   |   |-- test_image_document.py
|   |   |   |   |   |-- test_media_resource.py
|   |   |   |   |   |-- test_node.py
|   |   |   |   |   \-- test_schema.py
|   |   |   |   |-- selectors
|   |   |   |   |   \-- test_llm_selectors.py
|   |   |   |   |-- sparse_embeddings
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_mock_sparse_embeddings.py
|   |   |   |   |-- storage
|   |   |   |   |   |-- chat_store
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_simple_chat_store.py
|   |   |   |   |   |   |-- test_sql.py
|   |   |   |   |   |   \-- test_sql_schema.py
|   |   |   |   |   |-- docstore
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_legacy_json_to_doc.py
|   |   |   |   |   |   \-- test_simple_docstore.py
|   |   |   |   |   |-- index_store
|   |   |   |   |   |   \-- test_simple_index_store.py
|   |   |   |   |   |-- kvstore
|   |   |   |   |   |   |-- test_mutable_mapping_kvstore.py
|   |   |   |   |   |   \-- test_simple_kvstore.py
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- conftest.py
|   |   |   |   |   \-- test_storage_context.py
|   |   |   |   |-- text_splitter
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- conftest.py
|   |   |   |   |   |-- test_code_splitter.py
|   |   |   |   |   |-- test_sentence_splitter.py
|   |   |   |   |   \-- test_token_splitter.py
|   |   |   |   |-- token_predictor
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_base.py
|   |   |   |   |-- tools
|   |   |   |   |   |-- tool_spec
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_base.py
|   |   |   |   |   |   \-- test_load_and_search.py
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- conftest.py
|   |   |   |   |   |-- test_base.py
|   |   |   |   |   |-- test_eval_query_engine_tool.py
|   |   |   |   |   |-- test_ondemand_loader.py
|   |   |   |   |   |-- test_query_engine_tool.py
|   |   |   |   |   |-- test_retriever_tool.py
|   |   |   |   |   |-- test_types.py
|   |   |   |   |   \-- test_utils.py
|   |   |   |   |-- utilities
|   |   |   |   |   \-- test_sql_wrapper.py
|   |   |   |   |-- vector_stores
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- test_simple.py
|   |   |   |   |   \-- test_utils.py
|   |   |   |   |-- voice_agents
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- test_event_serialization.py
|   |   |   |   |   \-- test_subclasses.py
|   |   |   |   |-- __init__.py
|   |   |   |   |-- conftest.py
|   |   |   |   |-- docker-compose.yml
|   |   |   |   |-- ruff.toml
|   |   |   |   |-- test_async_utils.py
|   |   |   |   |-- test_rate_limiter.py
|   |   |   |   |-- test_types.py
|   |   |   |   \-- test_utils.py
|   |   |   |-- .gitignore
|   |   |   |-- LICENSE
|   |   |   |-- Makefile
|   |   |   |-- pyproject.toml
|   |   |   |-- README.md
|   |   |   \-- uv.lock
|   |   |-- llama-index-experimental
|   |   |   |-- llama_index
|   |   |   |   \-- experimental
|   |   |   |       |-- nudge
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   \-- base.py
|   |   |   |       |-- param_tuner
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   \-- base.py
|   |   |   |       |-- query_engine
|   |   |   |       |   |-- jsonalyze
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   \-- jsonalyze_query_engine.py
|   |   |   |       |   |-- pandas
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- output_parser.py
|   |   |   |       |   |   |-- pandas_query_engine.py
|   |   |   |       |   |   \-- prompts.py
|   |   |   |       |   |-- polars
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- output_parser.py
|   |   |   |       |   |   |-- polars_query_engine.py
|   |   |   |       |   |   \-- prompts.py
|   |   |   |       |   \-- __init__.py
|   |   |   |       |-- retrievers
|   |   |   |       |   \-- natural_language
|   |   |   |       |       |-- __init__.py
|   |   |   |       |       |-- nl_csv_retriever.py
|   |   |   |       |       |-- nl_data_frame_retriever.py
|   |   |   |       |       |-- nl_json_retriever.py
|   |   |   |       |       \-- README.md
|   |   |   |       |-- __init__.py
|   |   |   |       \-- exec_utils.py
|   |   |   |-- tests
|   |   |   |   |-- __init__.py
|   |   |   |   |-- test_exec_utils.py
|   |   |   |   |-- test_pandas.py
|   |   |   |   \-- test_polars.py
|   |   |   |-- .gitignore
|   |   |   |-- LICENSE
|   |   |   |-- Makefile
|   |   |   |-- pyproject.toml
|   |   |   |-- README.md
|   |   |   \-- uv.lock
|   |   |-- llama-index-finetuning
|   |   |   |-- llama_index
|   |   |   |   \-- finetuning
|   |   |   |       |-- azure_openai
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   \-- base.py
|   |   |   |       |-- callbacks
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   \-- finetuning_handler.py
|   |   |   |       |-- cross_encoders
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- cross_encoder.py
|   |   |   |       |   \-- dataset_gen.py
|   |   |   |       |-- embeddings
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- adapter.py
|   |   |   |       |   |-- adapter_utils.py
|   |   |   |       |   |-- common.py
|   |   |   |       |   \-- sentence_transformer.py
|   |   |   |       |-- mistralai
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- base.py
|   |   |   |       |   \-- utils.py
|   |   |   |       |-- openai
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- base.py
|   |   |   |       |   \-- validate_json.py
|   |   |   |       |-- rerankers
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- cohere_reranker.py
|   |   |   |       |   \-- dataset_gen.py
|   |   |   |       |-- __init__.py
|   |   |   |       \-- types.py
|   |   |   |-- .gitignore
|   |   |   |-- LICENSE
|   |   |   |-- Makefile
|   |   |   |-- pyproject.toml
|   |   |   |-- README.md
|   |   |   \-- uv.lock
|   |   |-- llama-index-instrumentation
|   |   |   |-- src
|   |   |   |   \-- llama_index_instrumentation
|   |   |   |       |-- base
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- event.py
|   |   |   |       |   \-- handler.py
|   |   |   |       |-- event_handlers
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- base.py
|   |   |   |       |   \-- null.py
|   |   |   |       |-- events
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   \-- span.py
|   |   |   |       |-- span
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- base.py
|   |   |   |       |   \-- simple.py
|   |   |   |       |-- span_handlers
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- base.py
|   |   |   |       |   |-- null.py
|   |   |   |       |   \-- simple.py
|   |   |   |       |-- __init__.py
|   |   |   |       |-- dispatcher.py
|   |   |   |       \-- py.typed
|   |   |   |-- tests
|   |   |   |   |-- test_dispatcher.py
|   |   |   |   \-- test_manager.py
|   |   |   |-- .gitignore
|   |   |   |-- pyproject.toml
|   |   |   |-- README.md
|   |   |   \-- uv.lock
|   |   |-- llama-index-integrations
|   |   |   |-- agent
|   |   |   |   |-- llama-index-agent-agentmesh
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- agent
|   |   |   |   |   |   |   |-- agentmesh
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- identity.py
|   |   |   |   |   |   |   |   |-- query_engine.py
|   |   |   |   |   |   |   |   |-- trust.py
|   |   |   |   |   |   |   |   \-- worker.py
|   |   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   \-- README.md
|   |   |   |   \-- llama-index-agent-azure
|   |   |   |       |-- llama_index
|   |   |   |       |   \-- agent
|   |   |   |       |       \-- azure_foundry_agent
|   |   |   |       |           |-- __init__.py
|   |   |   |       |           \-- base.py
|   |   |   |       |-- tests
|   |   |   |       |   \-- test_azure_foundry_agent.py
|   |   |   |       |-- .gitignore
|   |   |   |       |-- Makefile
|   |   |   |       |-- pyproject.toml
|   |   |   |       \-- README.md
|   |   |   |-- callbacks
|   |   |   |   |-- llama-index-callbacks-agentops
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- callbacks
|   |   |   |   |   |       \-- agentops
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-callbacks-aim
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- callbacks
|   |   |   |   |   |       \-- aim
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-callbacks-argilla
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- callbacks
|   |   |   |   |   |       \-- argilla
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-callbacks-arize-phoenix
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- callbacks
|   |   |   |   |   |       \-- arize_phoenix
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-callbacks-honeyhive
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- callbacks
|   |   |   |   |   |       \-- honeyhive
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-callbacks-langfuse
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- callbacks
|   |   |   |   |   |       \-- langfuse
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-callbacks-literalai
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- literalai_example.py
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- callbacks
|   |   |   |   |   |       \-- literalai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-callbacks-openinference
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- callbacks
|   |   |   |   |   |       \-- openinference
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_openinference_callback.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-callbacks-opik
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- opik_example.py
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- callbacks
|   |   |   |   |   |       \-- opik
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-callbacks-promptlayer
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- callbacks
|   |   |   |   |   |       \-- promptlayer
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_promptlayer_callback.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-callbacks-uptrain
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- callbacks
|   |   |   |   |   |       \-- uptrain
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_uptrain_callback.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   \-- llama-index-callbacks-wandb
|   |   |   |       |-- llama_index
|   |   |   |       |   \-- callbacks
|   |   |   |       |       \-- wandb
|   |   |   |       |           |-- __init__.py
|   |   |   |       |           \-- base.py
|   |   |   |       |-- tests
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   \-- test_wandb_callback.py
|   |   |   |       |-- LICENSE
|   |   |   |       |-- Makefile
|   |   |   |       |-- pyproject.toml
|   |   |   |       |-- README.md
|   |   |   |       \-- uv.lock
|   |   |   |-- embeddings
|   |   |   |   |-- llama-index-embeddings-adapter
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- adapter
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_adapter.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-alephalpha
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- alephalpha
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_alephalpha.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-alibabacloud-aisearch
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- alibabacloud_aisearch
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_alibabacloud_aisearch.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-anyscale
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- anyscale
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_anyscale_embedding.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-autoembeddings
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- autoembeddings
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_autoembeddings.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- MAKEFILE
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-azure-inference
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- azure_inference
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_azure_inference.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-azure-openai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- azure_openai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-baseten
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- baseten
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-bedrock
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- bedrock
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_bedrock.py
|   |   |   |   |   |   |-- test_bedrock_async.py
|   |   |   |   |   |   \-- test_bedrock_embedding.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-clarifai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- clarifai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-clip
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- clip
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_clip.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-cloudflare-workersai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- cloudflare_workersai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_cloudflare-workersai.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-cohere
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- cohere
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   \-- test_embeddings.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-dashscope
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- dashscope
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_dashscope.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-databricks
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- databricks
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_embeddings_databricks.py
|   |   |   |   |   |   \-- test_integration_databricks.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-deepinfra
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- deepinfra
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_deepinfra.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-elasticsearch
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- elasticsearch
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_elasticsearch.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- docker-compose.yml
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-fastembed
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- fastembed
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_fastembed.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-fireworks
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- fireworks
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-gaudi
|   |   |   |   |   |-- examples
|   |   |   |   |   |   |-- basic.py
|   |   |   |   |   |   |-- graphrag.py
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- requirements.txt
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- gaudi
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-gigachat
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- gigachat
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_gigachat.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-google-genai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- google_genai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_gemini.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-heroku
|   |   |   |   |   |-- examples
|   |   |   |   |   |   |-- async_usage.py
|   |   |   |   |   |   \-- basic_usage.py
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- heroku
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_heroku_embeddings.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-huggingface
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- huggingface
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           |-- pooling.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_embeddings_huggingface.py
|   |   |   |   |   |   |-- test_hf_inference.py
|   |   |   |   |   |   \-- test_hf_utils.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-huggingface-api
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- huggingface_api
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- pooling.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_embeddings_huggingface.py
|   |   |   |   |   |   \-- test_hf_inference.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-huggingface-openvino
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- huggingface_openvino
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-huggingface-optimum
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- huggingface_optimum
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_huggingface_optimum.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-huggingface-optimum-intel
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- huggingface_optimum_intel
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_huggingface_optimum_intel.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-ibm
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- ibm
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_embeddings_ibm.py
|   |   |   |   |   |   \-- test_ibm.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-instructor
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- instructor
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-ipex-llm
|   |   |   |   |   |-- examples
|   |   |   |   |   |   |-- basic.py
|   |   |   |   |   |   \-- README.md
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- ipex_llm
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   \-- README.md
|   |   |   |   |-- llama-index-embeddings-isaacus
|   |   |   |   |   |-- examples
|   |   |   |   |   |   |-- async_usage.py
|   |   |   |   |   |   \-- basic_usage.py
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- isaacus
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_isaacus_embeddings.py
|   |   |   |   |   |-- .env.example
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-jinaai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- jinaai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_jinaai.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-langchain
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- langchain
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_langchain.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-litellm
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       |-- litellm
|   |   |   |   |   |       |   |-- __init__.py
|   |   |   |   |   |       |   \-- base.py
|   |   |   |   |   |       \-- __init__.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_litellm.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-llamafile
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- llamafile
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_llamafile.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-llm-rails
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- llm_rails
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_llm_rails.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-mistralai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- mistralai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_mistralai.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-mixedbreadai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- mixedbreadai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   \-- test_embeddings_mixedbreadai.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-modelscope
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- modelscope
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   \-- test_modelscope.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-nebius
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- nebius
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_nebius.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-netmind
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- netmind
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_netmind.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-nomic
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- nomic
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_nomic.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-nvidia
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- nvidia
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_api_key.py
|   |   |   |   |   |   |-- test_available_models.py
|   |   |   |   |   |   |-- test_base_url.py
|   |   |   |   |   |   |-- test_embeddings_nvidia.py
|   |   |   |   |   |   |-- test_integration.py
|   |   |   |   |   |   \-- test_truncate.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-oci-data-science
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- oci_data_science
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           |-- client.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_embeddings_oci_data_science.py
|   |   |   |   |   |   \-- test_oci_data_science_client.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-oci-genai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- oci_genai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_embeddings_oci_genai.py
|   |   |   |   |   |   \-- test_oci_genai.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-ollama
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- ollama
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_ollama.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-opea
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- opea
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-openai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- openai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_embeddings_openai.py
|   |   |   |   |   |   \-- test_utils.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-openai-like
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- openai_like
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_openai_like.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-openvino-genai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- openvino_genai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-oracleai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- oracleai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_oracleai.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-premai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- premai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           |-- pyproject.toml
|   |   |   |   |   |           \-- uv.lock
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-sagemaker-endpoint
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- sagemaker_endpoint
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_sagemaker_endpoint.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-siliconflow
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- siliconflow
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   \-- test_embeddings_siliconflow.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-text-embeddings-inference
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- text_embeddings_inference
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_text_embeddings_inference.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-textembed
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- textembed
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_textembed.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-together
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- together
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_together.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-upstage
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- upstage
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- integration_tests
|   |   |   |   |   |   |   \-- test_integrations.py
|   |   |   |   |   |   |-- unit_tests
|   |   |   |   |   |   |   \-- test_embeddings_upstage.py
|   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-vertex
|   |   |   |   |   |-- examples
|   |   |   |   |   |   |-- multimodal_embedding.ipynb
|   |   |   |   |   |   \-- text_embedding.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- vertex
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_vertex.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-vertex-endpoint
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- vertex_endpoint
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_vertex_endpoint.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-vllm
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- vllm
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_vllm.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-voyageai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- voyageai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_embeddings_voyageai.py
|   |   |   |   |   |   \-- test_embeddings_voyageai_integration.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-xinference
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- xinference
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_xinference.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-embeddings-yandexgpt
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- embeddings
|   |   |   |   |   |       \-- yandexgpt
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- util.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_embeddings_yandexgpt.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   \-- llama-index-embeddings-zhipuai
|   |   |   |       |-- llama_index
|   |   |   |       |   \-- embeddings
|   |   |   |       |       \-- zhipuai
|   |   |   |       |           |-- __init__.py
|   |   |   |       |           \-- base.py
|   |   |   |       |-- tests
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   \-- test_embeddings_zhipuai.py
|   |   |   |       |-- .gitignore
|   |   |   |       |-- LICENSE
|   |   |   |       |-- Makefile
|   |   |   |       |-- pyproject.toml
|   |   |   |       |-- README.md
|   |   |   |       \-- uv.lock
|   |   |   |-- evaluation
|   |   |   |   \-- llama-index-evaluation-tonic-validate
|   |   |   |       |-- llama_index
|   |   |   |       |   \-- evaluation
|   |   |   |       |       \-- tonic_validate
|   |   |   |       |           |-- __init__.py
|   |   |   |       |           |-- answer_consistency.py
|   |   |   |       |           |-- answer_consistency_binary.py
|   |   |   |       |           |-- answer_similarity.py
|   |   |   |       |           |-- augmentation_accuracy.py
|   |   |   |       |           |-- augmentation_precision.py
|   |   |   |       |           |-- retrieval_precision.py
|   |   |   |       |           \-- tonic_validate_evaluator.py
|   |   |   |       |-- tests
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   \-- test_evaluation_tonic_validate.py
|   |   |   |       |-- .gitignore
|   |   |   |       |-- LICENSE
|   |   |   |       |-- Makefile
|   |   |   |       |-- pyproject.toml
|   |   |   |       |-- README.md
|   |   |   |       \-- uv.lock
|   |   |   |-- extractors
|   |   |   |   |-- llama-index-extractors-entity
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- extractors
|   |   |   |   |   |       \-- entity
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_extractors_entity.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-extractors-marvin
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- extractors
|   |   |   |   |   |       \-- marvin
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_extractors_marvin.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   \-- llama-index-extractors-relik
|   |   |   |       |-- llama_index
|   |   |   |       |   \-- extractors
|   |   |   |       |       \-- relik
|   |   |   |       |           |-- __init__.py
|   |   |   |       |           \-- base.py
|   |   |   |       |-- .gitignore
|   |   |   |       |-- LICENSE
|   |   |   |       |-- Makefile
|   |   |   |       |-- pyproject.toml
|   |   |   |       |-- README.md
|   |   |   |       \-- uv.lock
|   |   |   |-- graph_rag
|   |   |   |   \-- llama-index-graph-rag-cognee
|   |   |   |       |-- llama_index
|   |   |   |       |   \-- graph_rag
|   |   |   |       |       \-- cognee
|   |   |   |       |           |-- __init__.py
|   |   |   |       |           |-- base.py
|   |   |   |       |           \-- graph_rag.py
|   |   |   |       |-- tests
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- test_add_data.py
|   |   |   |       |   |-- test_graph_rag_cognee.py
|   |   |   |       |   \-- test_visualize_graph.py
|   |   |   |       |-- .gitignore
|   |   |   |       |-- example.py
|   |   |   |       |-- graph_visualization.html
|   |   |   |       |-- LICENSE
|   |   |   |       |-- Makefile
|   |   |   |       |-- pyproject.toml
|   |   |   |       |-- README.md
|   |   |   |       \-- uv.lock
|   |   |   |-- graph_stores
|   |   |   |   |-- llama-index-graph-stores-ApertureDB
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- graph_stores
|   |   |   |   |   |       \-- ApertureDB
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- property_graph.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   \-- test_pg_stores_ApertureDB.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   \-- README.md
|   |   |   |   |-- llama-index-graph-stores-falkordb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- graph_stores
|   |   |   |   |   |       \-- falkordb
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- falkordb_property_graph.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_graph_stores_falkordb.py
|   |   |   |   |   |   \-- test_pg_stores_falkordb.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-graph-stores-memgraph
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- graph_stores
|   |   |   |   |   |       \-- memgraph
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- kg_base.py
|   |   |   |   |   |           \-- property_graph.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_graph_stores_memgraph.py
|   |   |   |   |   |   \-- test_pg_stores_memgraph.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-graph-stores-nebula
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- a.py
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- graph_stores
|   |   |   |   |   |       \-- nebula
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- nebula_graph_store.py
|   |   |   |   |   |           |-- nebula_property_graph.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_graph_stores_nebula.py
|   |   |   |   |   |   \-- test_property_graph.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-graph-stores-neo4j
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- graph_stores
|   |   |   |   |   |       \-- neo4j
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           |-- cypher_corrector.py
|   |   |   |   |   |           \-- neo4j_property_graph.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_graph_stores_neo4j.py
|   |   |   |   |   |   \-- test_pg_stores_neo4j.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-graph-stores-neptune
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- graph_stores
|   |   |   |   |   |       \-- neptune
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- analytics.py
|   |   |   |   |   |           |-- analytics_property_graph.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           |-- base_property_graph.py
|   |   |   |   |   |           |-- database.py
|   |   |   |   |   |           |-- database_property_graph.py
|   |   |   |   |   |           \-- neptune.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_graph_stores_neptune.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   \-- llama-index-graph-stores-tidb
|   |   |   |       |-- llama_index
|   |   |   |       |   \-- graph_stores
|   |   |   |       |       \-- tidb
|   |   |   |       |           |-- __init__.py
|   |   |   |       |           |-- graph.py
|   |   |   |       |           |-- property_graph.py
|   |   |   |       |           \-- utils.py
|   |   |   |       |-- tests
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- test_graph_stores_tidb.py
|   |   |   |       |   \-- test_property_graph_stores_tidb.py
|   |   |   |       |-- .gitignore
|   |   |   |       |-- LICENSE
|   |   |   |       |-- Makefile
|   |   |   |       |-- pyproject.toml
|   |   |   |       |-- README.md
|   |   |   |       \-- uv.lock
|   |   |   |-- indices
|   |   |   |   |-- llama-index-indices-managed-bge-m3
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- indices
|   |   |   |   |   |       \-- managed
|   |   |   |   |   |           \-- bge_m3
|   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |               |-- base.py
|   |   |   |   |   |               \-- retriever.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-indices-managed-colbert
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- indices
|   |   |   |   |   |       \-- managed
|   |   |   |   |   |           \-- colbert
|   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |               |-- base.py
|   |   |   |   |   |               \-- retriever.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_indices_managed_colbert.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-indices-managed-dashscope
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- indices
|   |   |   |   |   |       \-- managed
|   |   |   |   |   |           \-- dashscope
|   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |               |-- api_utils.py
|   |   |   |   |   |               |-- base.py
|   |   |   |   |   |               |-- constants.py
|   |   |   |   |   |               |-- retriever.py
|   |   |   |   |   |               |-- transformations.py
|   |   |   |   |   |               \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_indices_managed_dashscope.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-indices-managed-google
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- indices
|   |   |   |   |   |       \-- managed
|   |   |   |   |   |           \-- google
|   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |               \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_indices_managed_google.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-indices-managed-lancedb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- indices
|   |   |   |   |   |   |   \-- managed
|   |   |   |   |   |   |       \-- lancedb
|   |   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |   |           |-- base.py
|   |   |   |   |   |   |           |-- query_engine.py
|   |   |   |   |   |   |           |-- retriever.py
|   |   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_index.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-indices-managed-llama-cloud
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- indices
|   |   |   |   |   |       \-- managed
|   |   |   |   |   |           \-- llama_cloud
|   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |               |-- api_utils.py
|   |   |   |   |   |               |-- base.py
|   |   |   |   |   |               |-- composite_retriever.py
|   |   |   |   |   |               \-- retriever.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- data
|   |   |   |   |   |   |   |-- image_figure_slides.pdf
|   |   |   |   |   |   |   \-- Simple PDF Slides.pdf
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_indices_managed_llama_cloud.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-indices-managed-postgresml
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- indices
|   |   |   |   |   |       \-- managed
|   |   |   |   |   |           \-- postgresml
|   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |               |-- base.py
|   |   |   |   |   |               |-- query.py
|   |   |   |   |   |               \-- retriever.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_indices_managed_postgresml.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-indices-managed-vectara
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- indices
|   |   |   |   |   |       \-- managed
|   |   |   |   |   |           \-- vectara
|   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |               |-- base.py
|   |   |   |   |   |               |-- prompts.py
|   |   |   |   |   |               |-- query.py
|   |   |   |   |   |               \-- retriever.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_indices_managed_vectara.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- Changelog.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   \-- llama-index-indices-managed-vertexai
|   |   |   |       |-- llama_index
|   |   |   |       |   \-- indices
|   |   |   |       |       \-- managed
|   |   |   |       |           \-- vertexai
|   |   |   |       |               |-- __init__.py
|   |   |   |       |               |-- base.py
|   |   |   |       |               \-- retriever.py
|   |   |   |       |-- tests
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   \-- test_indices_managed_vertexai.py
|   |   |   |       |-- .gitignore
|   |   |   |       |-- LICENSE
|   |   |   |       |-- Makefile
|   |   |   |       |-- pyproject.toml
|   |   |   |       |-- README.md
|   |   |   |       \-- uv.lock
|   |   |   |-- ingestion
|   |   |   |   \-- llama-index-ingestion-ray
|   |   |   |       |-- llama_index
|   |   |   |       |   \-- ingestion
|   |   |   |       |       \-- ray
|   |   |   |       |           |-- __init__.py
|   |   |   |       |           |-- base.py
|   |   |   |       |           |-- transform.py
|   |   |   |       |           \-- utils.py
|   |   |   |       |-- tests
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   \-- test_pipeline.py
|   |   |   |       |-- .gitignore
|   |   |   |       |-- LICENSE
|   |   |   |       |-- Makefile
|   |   |   |       |-- pyproject.toml
|   |   |   |       |-- README.md
|   |   |   |       \-- uv.lock
|   |   |   |-- llms
|   |   |   |   |-- llama-index-llms-ai21
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- ai21
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   \-- test_llms_ai21.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-aibadgr
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- aibadgr
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_aibadgr.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   \-- README.md
|   |   |   |   |-- llama-index-llms-alephalpha
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- alephalpha
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_alephalpha.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-alibabacloud-aisearch
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- alibabacloud_aisearch
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_alibabacloud_aisearch.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-anthropic
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- anthropic
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           |-- py.typed
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_anthropic_utils.py
|   |   |   |   |   |   \-- test_llms_anthropic.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-anyscale
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- anyscale
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_anyscale.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-apertis
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- apertis
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_apertis.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-asi
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- asi
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_integration_asi.py
|   |   |   |   |   |   \-- test_llms_asi.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-azure-inference
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- azure_inference
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_azure_inference.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-azure-openai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- azure_openai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_azure_openai.py
|   |   |   |   |   |   \-- test_llms_azure_openai.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-baseten
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- baseten
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           |-- BUILD
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_baseten_dynamic.py
|   |   |   |   |   |   |-- test_coverage_comprehensive.py
|   |   |   |   |   |   \-- test_llms_baseten.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- BUILD
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-bedrock
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- bedrock
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           |-- llama_utils.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_bedrock.py
|   |   |   |   |   |   |-- test_llms_bedrock.py
|   |   |   |   |   |   \-- test_utils.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-bedrock-converse
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- bedrock_converse
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_bedrock_converse_utils.py
|   |   |   |   |   |   |-- test_llms_bedrock_converse.py
|   |   |   |   |   |   \-- test_thinking_delta.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-cerebras
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- cerebras
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_integration_cerebras.py
|   |   |   |   |   |   \-- test_llms_cerebras.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-clarifai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- clarifai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-cleanlab
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- cleanlab
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_cleanlab.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-cloudflare-ai-gateway
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- cloudflare_ai_gateway
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- providers.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_cloudflare_ai_gateway.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- env.example
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-cohere
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- cohere
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_llms_cohere.py
|   |   |   |   |   |   \-- test_rag_inference.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-cometapi
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- cometapi
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_cometapi.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-contextual
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- contextual
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- test-contextual.ipynb
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_empty.py
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-cortex
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- cortex
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_integration_cortex.py
|   |   |   |   |   |   |-- test_llms_cortex.py
|   |   |   |   |   |   \-- test_utils.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-dashscope
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- dashscope
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_dashscope.py
|   |   |   |   |   |   \-- test_llms_dashscope.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-databricks
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- databricks
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_integration_databricks.py
|   |   |   |   |   |   \-- test_llms_databricks.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-deepinfra
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- deepinfra
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           |-- client.py
|   |   |   |   |   |           |-- constants.py
|   |   |   |   |   |           |-- types.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_deepinfra.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-deepseek
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- deepseek
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_deepseek.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-everlyai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- everlyai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_everlyai.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-featherlessai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- featherlessai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_featherlessai.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-fireworks
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- fireworks
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_fireworks.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-friendli
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- friendli
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_friendli.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-gaudi
|   |   |   |   |   |-- examples
|   |   |   |   |   |   |-- basic.py
|   |   |   |   |   |   \-- README.md
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- gaudi
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-gigachat
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- gigachat
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   \-- test_llms_gigachat.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-google-genai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- google_genai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           |-- py.typed
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_base_cleanup.py
|   |   |   |   |   |   |-- test_llms_google_genai.py
|   |   |   |   |   |   \-- test_llms_google_genai_vertex.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-groq
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- groq
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_integration_groq.py
|   |   |   |   |   |   \-- test_llms_groq.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-helicone
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- helicone
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_helicone.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-heroku
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- heroku
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_api_key.py
|   |   |   |   |   |   \-- test_integration.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-huggingface
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- huggingface
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_huggingface.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-huggingface-api
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- huggingface_api
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_huggingface_api.py
|   |   |   |   |   |   \-- test_llms_huggingface_api.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-ibm
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- ibm
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_ibm.py
|   |   |   |   |   |   |-- test_llms_ibm.py
|   |   |   |   |   |   \-- test_tool_required.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-ipex-llm
|   |   |   |   |   |-- examples
|   |   |   |   |   |   |-- basic.py
|   |   |   |   |   |   |-- low_bit.py
|   |   |   |   |   |   |-- more_data_type.py
|   |   |   |   |   |   \-- README.md
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- ipex_llm
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   \-- README.md
|   |   |   |   |-- llama-index-llms-keywordsai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- keywordsai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_keywordsai.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-konko
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- konko
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_konko.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-langchain
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- langchain
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_langchain.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-litellm
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- litellm
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_llms_litellm.py
|   |   |   |   |   |   \-- test_utils.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-llama-api
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- llama_api
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_llama_api.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-llama-cpp
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- llama_cpp
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- llama_utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_llama_cpp.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-llamafile
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- llamafile
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_llamafile.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-lmstudio
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- lmstudio
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_lmstudio.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-localai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- localai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_localai.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-maritalk
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- maritalk
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-meta
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- meta
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_llama.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-mistral-rs
|   |   |   |   |   |-- examples
|   |   |   |   |   |   |-- plain.ipynb
|   |   |   |   |   |   |-- streaming.ipynb
|   |   |   |   |   |   \-- xlora_gguf.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- mistral_rs
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_mistral-rs.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-mistralai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- mistralai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_mistral.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-mlx
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- mlx
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           |-- tokenizer_utils.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-modelscope
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- modelscope
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_modelscope.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-modelslab
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- modelslab
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   \-- test_modelslab_llm.py
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   \-- README.md
|   |   |   |   |-- llama-index-llms-monsterapi
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- monsterapi
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_monsterapi.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-mymagic
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- mymagic
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-nebius
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- nebius
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_nebius.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-netmind
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- netmind
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_netmind.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-neutrino
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- neutrino
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_neutrino.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-novita
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- novita
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   \-- test_llms_novita.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-nvidia
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- nvidia
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_additional_kwargs.py
|   |   |   |   |   |   |-- test_api_key.py
|   |   |   |   |   |   |-- test_available_models.py
|   |   |   |   |   |   |-- test_base_url.py
|   |   |   |   |   |   |-- test_integration.py
|   |   |   |   |   |   |-- test_mode_switch.py
|   |   |   |   |   |   |-- test_nvidia.py
|   |   |   |   |   |   |-- test_structured_output.py
|   |   |   |   |   |   |-- test_text-completion.py
|   |   |   |   |   |   |-- test_tools.py
|   |   |   |   |   |   \-- test_unknown_models.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-nvidia-tensorrt
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- nvidia_tensorrt
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_nvidia_tensorrt.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-nvidia-triton
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- nvidia_triton
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_nvidia_triton.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-oci-data-science
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- oci_data_science
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           |-- client.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_llms_oci_data_science.py
|   |   |   |   |   |   |-- test_oci_data_science_client.py
|   |   |   |   |   |   \-- test_oci_data_science_utils.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-oci-genai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- oci_genai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_llms_oci_genai.py
|   |   |   |   |   |   \-- test_oci_genai.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-octoai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- octoai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_octoai.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-ollama
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- ollama
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_llms_ollama.py
|   |   |   |   |   |   \-- test_utils.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-opea
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- opea
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_opea.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-openai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- openai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           |-- py.typed
|   |   |   |   |   |           |-- responses.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_llms_openai.py
|   |   |   |   |   |   |-- test_openai.py
|   |   |   |   |   |   |-- test_openai_responses.py
|   |   |   |   |   |   \-- test_openai_utils.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-openai-like
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- openai_like
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_llms_openai_like.py
|   |   |   |   |   |   |-- test_openai_like.py
|   |   |   |   |   |   \-- test_openai_like_grok.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-openrouter
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- openrouter
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_openrouter.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-openvino
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- openvino
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-openvino-genai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- openvino_genai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-optimum-intel
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- optimum_intel
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-ovhcloud
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- ovhcloud
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           |-- BUILD
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_coverage_comprehensive.py
|   |   |   |   |   |   \-- test_llms_ovhcloud.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- BUILD
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   \-- README.md
|   |   |   |   |-- llama-index-llms-paieas
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- paieas
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_paieas.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-palm
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- palm
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_palm.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-perplexity
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- perplexity
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_llms_perplexity.py
|   |   |   |   |   |   \-- test_perplexity.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-pipeshift
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- pipeshift
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_pipeshift.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-portkey
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- portkey
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_portkey.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-predibase
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- predibase
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_predibase.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-premai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- premai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-qianfan
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- qianfan
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_qianfan.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-reka
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- reka
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_llms_reka.py
|   |   |   |   |   |   \-- test_reka.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- llama_index_reka_samplenotebook.ipynb
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-replicate
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- replicate
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_replicate.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-rungpt
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- rungpt
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_rungpt.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-sagemaker-endpoint
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- sagemaker_endpoint
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_sagemaker_endpoint.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-sambanovasystems
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- sambanovasystems
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   \-- test_llms_sambanovasystems.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-sarvam
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- sarvam
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_servam.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-sglang
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- sglang
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_sglang.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   \-- README.md
|   |   |   |   |-- llama-index-llms-siliconflow
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- siliconflow
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   \-- test_llms_siliconflow.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-stepfun
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- stepfun
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_stepfun.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-text-generation-inference
|   |   |   |   |   \-- README.md
|   |   |   |   |-- llama-index-llms-together
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- together
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_together.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-upstage
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- upstage
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_llms_upstage.py
|   |   |   |   |   |   \-- test_upstage.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-vercel-ai-gateway
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- vercel_ai_gateway
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vercel_ai_gateway.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-vertex
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- vertex
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           |-- gemini_utils.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_gemini_utils.py
|   |   |   |   |   |   |-- test_llms_vertex.py
|   |   |   |   |   |   \-- test_tool_required.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-vllm
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- vllm
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- cassettes
|   |   |   |   |   |   |   |-- TestVllmIntegration.test_achat.yaml
|   |   |   |   |   |   |   |-- TestVllmIntegration.test_acompletion.yaml
|   |   |   |   |   |   |   |-- TestVllmIntegration.test_astream_chat.yaml
|   |   |   |   |   |   |   |-- TestVllmIntegration.test_astream_completion.yaml
|   |   |   |   |   |   |   |-- TestVllmIntegration.test_chat.yaml
|   |   |   |   |   |   |   |-- TestVllmIntegration.test_completion.yaml
|   |   |   |   |   |   |   |-- TestVllmIntegration.test_stream_chat.yaml
|   |   |   |   |   |   |   \-- TestVllmIntegration.test_stream_completion.yaml
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_integration.py
|   |   |   |   |   |   |-- test_llms_vllm.py
|   |   |   |   |   |   \-- test_vllm_server_modes.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-xinference
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- xinference
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_xinference.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-yi
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- yi
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_yi.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-llms-you
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- llms
|   |   |   |   |   |       \-- you
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_llms_you.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   \-- llama-index-llms-zhipuai
|   |   |   |       |-- llama_index
|   |   |   |       |   \-- llms
|   |   |   |       |       \-- zhipuai
|   |   |   |       |           |-- __init__.py
|   |   |   |       |           \-- base.py
|   |   |   |       |-- tests
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- conftest.py
|   |   |   |       |   \-- test_llms_zhipuai.py
|   |   |   |       |-- .gitignore
|   |   |   |       |-- LICENSE
|   |   |   |       |-- Makefile
|   |   |   |       |-- pyproject.toml
|   |   |   |       |-- README.md
|   |   |   |       \-- uv.lock
|   |   |   |-- memory
|   |   |   |   |-- llama-index-memory-bedrock-agentcore
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- memory
|   |   |   |   |   |       \-- bedrock_agentcore
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_agentcore_memory.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   \-- llama-index-memory-mem0
|   |   |   |       |-- llama_index
|   |   |   |       |   \-- memory
|   |   |   |       |       \-- mem0
|   |   |   |       |           |-- __init__.py
|   |   |   |       |           |-- base.py
|   |   |   |       |           \-- utils.py
|   |   |   |       |-- tests
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   \-- test_mem0.py
|   |   |   |       |-- .gitignore
|   |   |   |       |-- LICENSE
|   |   |   |       |-- Makefile
|   |   |   |       |-- pyproject.toml
|   |   |   |       |-- README.md
|   |   |   |       \-- uv.lock
|   |   |   |-- node_parser
|   |   |   |   |-- llama-index-node-parser-alibabacloud-aisearch
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- node_parser
|   |   |   |   |   |       \-- alibabacloud_aisearch
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_node_parser_alibabacloud_aisearch.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-node-parser-chonkie
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- node_parser
|   |   |   |   |   |       \-- chonkie
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- chunkers.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_chunkers.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   \-- README.md
|   |   |   |   |-- llama-index-node-parser-docling
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- node_parser
|   |   |   |   |   |       \-- docling
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- data
|   |   |   |   |   |   |   |-- inp_li_doc.json
|   |   |   |   |   |   |   |-- out_get_nodes_from_docs.json
|   |   |   |   |   |   |   \-- out_parse_nodes.json
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_node_parser_docling.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-node-parser-relational-dashscope
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- node_parser
|   |   |   |   |   |       \-- dashscope
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_node_parser_relational_dashscope.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-node-parser-slide
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- node_parser
|   |   |   |   |   |       \-- slide
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_node_parser_slide.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   \-- README.md
|   |   |   |   \-- llama-index-node-parser-topic
|   |   |   |       |-- llama_index
|   |   |   |       |   \-- node_parser
|   |   |   |       |       \-- topic
|   |   |   |       |           |-- __init__.py
|   |   |   |       |           \-- base.py
|   |   |   |       |-- tests
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   \-- test_node_parser_topic.py
|   |   |   |       |-- .gitignore
|   |   |   |       |-- LICENSE
|   |   |   |       |-- Makefile
|   |   |   |       |-- pyproject.toml
|   |   |   |       |-- README.md
|   |   |   |       \-- uv.lock
|   |   |   |-- observability
|   |   |   |   \-- llama-index-observability-otel
|   |   |   |       |-- llama_index
|   |   |   |       |   \-- observability
|   |   |   |       |       \-- otel
|   |   |   |       |           |-- __init__.py
|   |   |   |       |           |-- base.py
|   |   |   |       |           \-- utils.py
|   |   |   |       |-- tests
|   |   |   |       |   \-- test_otel.py
|   |   |   |       |-- .gitignore
|   |   |   |       |-- LICENSE
|   |   |   |       |-- Makefile
|   |   |   |       |-- pyproject.toml
|   |   |   |       |-- README.md
|   |   |   |       \-- uv.lock
|   |   |   |-- output_parsers
|   |   |   |   |-- llama-index-output-parsers-guardrails
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- output_parsers
|   |   |   |   |   |       \-- guardrails
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_output_parsers_guardrails.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   \-- llama-index-output-parsers-langchain
|   |   |   |       |-- llama_index
|   |   |   |       |   \-- output_parsers
|   |   |   |       |       \-- langchain
|   |   |   |       |           |-- __init__.py
|   |   |   |       |           \-- base.py
|   |   |   |       |-- tests
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   \-- test_output_parsers_langchain.py
|   |   |   |       |-- .gitignore
|   |   |   |       |-- LICENSE
|   |   |   |       |-- Makefile
|   |   |   |       |-- pyproject.toml
|   |   |   |       |-- README.md
|   |   |   |       \-- uv.lock
|   |   |   |-- postprocessor
|   |   |   |   |-- llama-index-postprocessor-aimon-rerank
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- postprocessor
|   |   |   |   |   |       \-- aimon_rerank
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_postprocessor_aimon_rerank.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-postprocessor-alibabacloud-aisearch-rerank
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- postprocessor
|   |   |   |   |   |       \-- alibabacloud_aisearch_rerank
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_postprocessor_alibabacloud_aisearch_rerank.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-postprocessor-bedrock-rerank
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- postprocessor
|   |   |   |   |   |       \-- bedrock_rerank
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_postprocessor_bedrock_rerank.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-postprocessor-cohere-rerank
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- postprocessor
|   |   |   |   |   |       \-- cohere_rerank
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_postprocessor_cohere_rerank.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-postprocessor-colbert-rerank
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- postprocessor
|   |   |   |   |   |       \-- colbert_rerank
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   \-- test_postprocessor_colbert_rerank.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-postprocessor-colpali-rerank
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- postprocessor
|   |   |   |   |   |       \-- colpali_rerank
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   \-- test_postprocessor_colpali_rerank.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-postprocessor-contextual-rerank
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- postprocessor
|   |   |   |   |   |       \-- contextual_rerank
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   \-- test_contextual_rerank.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-postprocessor-dashscope-rerank
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- postprocessor
|   |   |   |   |   |       \-- dashscope_rerank
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_postprocessor_dashscope_rerank.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-postprocessor-flag-embedding-reranker
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- postprocessor
|   |   |   |   |   |       \-- flag_embedding_reranker
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_postprocessor_flag_embedding_reranker.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-postprocessor-flashrank-rerank
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- postprocessor
|   |   |   |   |   |       \-- flashrank_rerank
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_postprocessor_flashrank_rerank.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-postprocessor-ibm
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- postprocessor
|   |   |   |   |   |       \-- ibm
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_ibm.py
|   |   |   |   |   |   \-- test_postprocessor_ibm_rerank.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-postprocessor-jinaai-rerank
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- postprocessor
|   |   |   |   |   |       \-- jinaai_rerank
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_postprocessor_jinaai_rerank.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-postprocessor-longllmlingua
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- longllmlingua2.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- postprocessor
|   |   |   |   |   |       \-- longllmlingua
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_postprocessor_longllmlingua.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-postprocessor-mixedbreadai-rerank
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- postprocessor
|   |   |   |   |   |       \-- mixedbreadai_rerank
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_postprocessor_mixedbreadai_rerank.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-postprocessor-nvidia-rerank
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- postprocessor
|   |   |   |   |   |       \-- nvidia_rerank
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_api_key.py
|   |   |   |   |   |   |-- test_available_models.py
|   |   |   |   |   |   |-- test_base_url.py
|   |   |   |   |   |   |-- test_postprocessor_nvidia_rerank.py
|   |   |   |   |   |   \-- test_truncate.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-postprocessor-openvino-rerank
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- postprocessor
|   |   |   |   |   |       \-- openvino_rerank
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-postprocessor-pinecone-native-rerank
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- postprocessor
|   |   |   |   |   |       \-- pinecone_native_rerank
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_pinecone_native_reranker.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-postprocessor-presidio
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- postprocessor
|   |   |   |   |   |       \-- presidio
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_postprocessor_presidio.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-postprocessor-rankgpt-rerank
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- postprocessor
|   |   |   |   |   |       \-- rankgpt_rerank
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_postprocessor_rankgpt_rerank.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-postprocessor-rankllm-rerank
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- rankLLM.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- postprocessor
|   |   |   |   |   |       \-- rankllm_rerank
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_postprocessor_rankllm-rerank.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-postprocessor-sbert-rerank
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- postprocessor
|   |   |   |   |   |       \-- sbert_rerank
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_postprocessor_sbert_rerank.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-postprocessor-siliconflow-rerank
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- postprocessor
|   |   |   |   |   |       \-- siliconflow_rerank
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_postprocessor_siliconflow_rerank.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-postprocessor-tei-rerank
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- postprocessor
|   |   |   |   |   |       \-- tei_rerank
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_postprocessor_tei_rerank.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-postprocessor-voyageai-rerank
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- postprocessor
|   |   |   |   |   |       \-- voyageai_rerank
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_postprocessor_voyageai-rerank.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   \-- llama-index-postprocessor-xinference-rerank
|   |   |   |       |-- llama_index
|   |   |   |       |   \-- postprocessor
|   |   |   |       |       \-- xinference_rerank
|   |   |   |       |           |-- __init__.py
|   |   |   |       |           \-- base.py
|   |   |   |       |-- tests
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   \-- test_postprocessor_xinference_rerank.py
|   |   |   |       |-- .gitignore
|   |   |   |       |-- LICENSE
|   |   |   |       |-- Makefile
|   |   |   |       |-- pyproject.toml
|   |   |   |       |-- README.md
|   |   |   |       \-- uv.lock
|   |   |   |-- program
|   |   |   |   |-- llama-index-program-evaporate
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- program
|   |   |   |   |   |       \-- evaporate
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           |-- df.py
|   |   |   |   |   |           |-- extractor.py
|   |   |   |   |   |           \-- prompts.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_program_evaporate.py
|   |   |   |   |   |   \-- test_sandbox.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-program-guidance
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- program
|   |   |   |   |   |       \-- guidance
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_program_guidance.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   \-- llama-index-program-lmformatenforcer
|   |   |   |       |-- llama_index
|   |   |   |       |   \-- program
|   |   |   |       |       \-- lmformatenforcer
|   |   |   |       |           |-- __init__.py
|   |   |   |       |           |-- base.py
|   |   |   |       |           \-- utils.py
|   |   |   |       |-- tests
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   \-- test_program_lmformatenforcer.py
|   |   |   |       |-- .gitignore
|   |   |   |       |-- LICENSE
|   |   |   |       |-- Makefile
|   |   |   |       |-- pyproject.toml
|   |   |   |       |-- README.md
|   |   |   |       \-- uv.lock
|   |   |   |-- protocols
|   |   |   |   \-- llama-index-protocols-ag-ui
|   |   |   |       |-- llama_index
|   |   |   |       |   \-- protocols
|   |   |   |       |       \-- ag_ui
|   |   |   |       |           |-- __init__.py
|   |   |   |       |           |-- agent.py
|   |   |   |       |           |-- events.py
|   |   |   |       |           |-- router.py
|   |   |   |       |           \-- utils.py
|   |   |   |       |-- LICENSE
|   |   |   |       |-- Makefile
|   |   |   |       |-- pyproject.toml
|   |   |   |       |-- README.md
|   |   |   |       \-- uv.lock
|   |   |   |-- question_gen
|   |   |   |   \-- llama-index-question-gen-guidance
|   |   |   |       |-- llama_index
|   |   |   |       |   \-- question_gen
|   |   |   |       |       \-- guidance
|   |   |   |       |           |-- __init__.py
|   |   |   |       |           \-- base.py
|   |   |   |       |-- tests
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   \-- test_question_gen_guidance_generator.py
|   |   |   |       |-- .gitignore
|   |   |   |       |-- LICENSE
|   |   |   |       |-- Makefile
|   |   |   |       |-- pyproject.toml
|   |   |   |       |-- README.md
|   |   |   |       \-- uv.lock
|   |   |   |-- readers
|   |   |   |   |-- llama-index-readers-agent-search
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- agent_search
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-airbyte-cdk
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- airbyte_cdk
|   |   |   |   |   |           |-- .gitignore
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_airbyte_cdk.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-airbyte-gong
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- airbyte_gong
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_airbyte_gong.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-airbyte-hubspot
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- airbyte_hubspot
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_airbyte_hubspot.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-airbyte-salesforce
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- airbyte_salesforce
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_airbyte_salesforce.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-airbyte-shopify
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- airbyte_shopify
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_airbyte_shopify.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-airbyte-stripe
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- airbyte_stripe
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_airbyte_stripe.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-airbyte-typeform
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- airbyte_typeform
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_airbyte_typeform.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-airbyte-zendesk-support
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- airbyte_zendesk_support
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_airbyte_zendesk_support.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-airtable
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- airtable
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-alibabacloud-aisearch
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- alibabacloud_aisearch
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_alibabacloud_aisearch.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-apify
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- apify
|   |   |   |   |   |           |-- actor
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           |-- dataset
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           \-- __init__.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_apify.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-arango-db
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- arango_db
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_arangodb.py
|   |   |   |   |   |   \-- test_readers_arango_db.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-asana
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- asana
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-assemblyai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- assemblyai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-astra-db
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- astra_db
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_astra_db.py
|   |   |   |   |   |   \-- test_readers_astra_db.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-athena
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- athena
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-awadb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- awadb
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_awadb.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-azcognitive-search
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- azcognitive_search
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_azcognitive_search.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-azstorage-blob
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- azstorage_blob
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_azstorage_blob.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-bagel
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- bagel
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_bagel.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-bilibili
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- bilibili
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-bitbucket
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- bitbucket
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_bitbucket.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-boarddocs
|   |   |   |   |   |-- examples
|   |   |   |   |   |   |-- BoardDocsReader.ipynb
|   |   |   |   |   |   \-- crawl.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- boarddocs
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-box
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- box_reader.py
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- box
|   |   |   |   |   |           |-- BoxAPI
|   |   |   |   |   |           |   |-- __init.py__
|   |   |   |   |   |           |   |-- box_api.py
|   |   |   |   |   |           |   \-- box_llama_adaptors.py
|   |   |   |   |   |           |-- BoxReader
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   \-- README.md
|   |   |   |   |   |           |-- BoxReaderAIExtraction
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   \-- README.md
|   |   |   |   |   |           |-- BoxReaderAIPrompt
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   \-- README.md
|   |   |   |   |   |           |-- BoxReaderTextExtraction
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   \-- README.md
|   |   |   |   |   |           \-- __init__.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_readers_box_ai_extract.py
|   |   |   |   |   |   |-- test_readers_box_ai_prompt.py
|   |   |   |   |   |   |-- test_readers_box_jwt.py
|   |   |   |   |   |   |-- test_readers_box_reader.py
|   |   |   |   |   |   \-- test_readers_box_text_extraction.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-chatgpt-plugin
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- chatgpt_plugin
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_chatgpt_plugin.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-chroma
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- chroma
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_chroma.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-confluence
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- confluence
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           |-- event.py
|   |   |   |   |   |           \-- html_parser.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- run_basic_tests.py
|   |   |   |   |   |   |-- test_html_parser.py
|   |   |   |   |   |   |-- test_integration.py
|   |   |   |   |   |   |-- test_new_features.py
|   |   |   |   |   |   \-- test_readers_confluence.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-couchbase
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- couchbase
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_couchbase.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-couchdb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- couchdb
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-dad-jokes
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- dad_jokes
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_dad_jokes.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-dashscope
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- dashscope
|   |   |   |   |   |           |-- domain
|   |   |   |   |   |           |   |-- base_domains.py
|   |   |   |   |   |           |   \-- lease_domains.py
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_dashscope.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-dashvector
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- dashvector
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_dashvector.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-database
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- database
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_database.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-datasets
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- datasets
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_datasets.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-deeplake
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- deeplake
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_deeplake.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-discord
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- discord
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_discord_reader.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-docling
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- docling
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_docling.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-docstring-walker
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- docstringwalker_example.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- docstring_walker
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_docstring_walker.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-docugami
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- docugami.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- docugami
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_docugami.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-document360
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- document360.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- document360
|   |   |   |   |   |           |-- entities
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- article.py
|   |   |   |   |   |           |   |-- article_slim.py
|   |   |   |   |   |           |   |-- category.py
|   |   |   |   |   |           |   \-- project_version.py
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- errors.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_document360.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-earnings-call-transcript
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- earnings_call_transcript
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_earnings_call_transcript.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-elasticsearch
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- elasticsearch
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_elasticsearch.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-faiss
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- faiss
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_faiss.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-feedly-rss
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- feedly_rss
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_feedly_rss.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-feishu-docs
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- feishu_docs
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_feishu_docs.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-file
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- file
|   |   |   |   |   |           |-- docs
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           |-- epub
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           |-- flat
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           |-- html
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           |-- image
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           |-- image_caption
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           |-- image_deplot
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   |-- README.md
|   |   |   |   |   |           |   \-- requirements.txt
|   |   |   |   |   |           |-- image_vision_llm
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           |-- ipynb
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           |-- markdown
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           |-- mbox
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           |-- paged_csv
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   \-- README.md
|   |   |   |   |   |           |-- pymu_pdf
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   |-- README.md
|   |   |   |   |   |           |   \-- requirements.txt
|   |   |   |   |   |           |-- rtf
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   \-- README.md
|   |   |   |   |   |           |-- slides
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   |-- content_extractor.py
|   |   |   |   |   |           |   \-- image_extractor.py
|   |   |   |   |   |           |-- tabular
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           |-- unstructured
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   |-- README.md
|   |   |   |   |   |           |   \-- requirements.txt
|   |   |   |   |   |           |-- video_audio
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           |-- xml
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   \-- README.md
|   |   |   |   |   |           \-- __init__.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- generate_test_ppt.py
|   |   |   |   |   |   |-- test_docs.py
|   |   |   |   |   |   |-- test_file.py
|   |   |   |   |   |   |-- test_html_reader.py
|   |   |   |   |   |   |-- test_image_vision_llm.py
|   |   |   |   |   |   |-- test_markdown.py
|   |   |   |   |   |   |-- test_readers_file.py
|   |   |   |   |   |   |-- test_rtf.py
|   |   |   |   |   |   |-- test_slides.py
|   |   |   |   |   |   \-- test_xml.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-firebase-realtimedb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- firebase_realtimedb
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_firebase_realtimedb.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-firestore
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- firestore
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_firestore.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-gcs
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- gcs
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_gcs.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-genius
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- genius
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_genius.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-gitbook
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- gitbook
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- gitbook_client.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- fixtures
|   |   |   |   |   |   |   |-- page_content_response.json
|   |   |   |   |   |   |   |-- pages_response.json
|   |   |   |   |   |   |   \-- space_response.json
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_gitbook_client.py
|   |   |   |   |   |   \-- test_simple_gitbook_reader.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-github
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- github_app_example.py
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- github
|   |   |   |   |   |           |-- collaborators
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   \-- github_client.py
|   |   |   |   |   |           |-- issues
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   \-- github_client.py
|   |   |   |   |   |           |-- repository
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   |-- event.py
|   |   |   |   |   |           |   |-- github_client.py
|   |   |   |   |   |           |   \-- utils.py
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- github_app_auth.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- test_gh_base_url.py
|   |   |   |   |   |   |-- test_github_app_auth.py
|   |   |   |   |   |   |-- test_github_repository_reader.py
|   |   |   |   |   |   \-- test_github_repository_reader_selective.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- GITHUB_APP_QUICKSTART.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-gitlab
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- gitlab
|   |   |   |   |   |           |-- issues
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           |-- repository
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           \-- __init__.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- test_readers_gitlab_issues.py
|   |   |   |   |   |   \-- test_readers_gitlab_repository.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-google
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- google
|   |   |   |   |   |           |-- calendar
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   \-- README.md
|   |   |   |   |   |           |-- chat
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   \-- README.md
|   |   |   |   |   |           |-- docs
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   \-- README.md
|   |   |   |   |   |           |-- drive
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   \-- README.md
|   |   |   |   |   |           |-- gmail
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   \-- README.md
|   |   |   |   |   |           |-- keep
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   \-- README.md
|   |   |   |   |   |           |-- maps
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   \-- README.md
|   |   |   |   |   |           |-- sheets
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   \-- README.md
|   |   |   |   |   |           \-- __init__.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_readers_google_drive.py
|   |   |   |   |   |   \-- test_readers_google_maps.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-gpt-repo
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- gpt_repo
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_gpt_repo.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-graphdb-cypher
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- graphdb_cypher
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_graphdb_cypher.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-graphql
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- graphql
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_graphql.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-guru
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- guru
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_guru.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-hatena-blog
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- hatena_blog
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_hatena_blog.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-hubspot
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- hubspot
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_hubspot.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-huggingface-fs
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- huggingface_fs
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_huggingface.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-hwp
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- hwp
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_hwp.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-iceberg
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- iceberg
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_iceberg.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-igpt-email
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- igpt_email
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_igpt_email.py
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   \-- README.md
|   |   |   |   |-- llama-index-readers-imdb-review
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- imdb_review
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- scraper.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_imdb_review.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-intercom
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- intercom
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_intercom.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-jaguar
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- jaguar
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_jaguar.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-jira
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- jira
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_jira.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-joplin
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- joplin
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_joplin.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-json
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- json
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_json.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-kaltura
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- kaltura_esearch
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_kaltura.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-kibela
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- kibela
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_kibela.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-layoutir
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- layoutir
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_layoutir.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   \-- README.md
|   |   |   |   |-- llama-index-readers-legacy-office
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- legacy_office
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- reader.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   \-- README.md
|   |   |   |   |-- llama-index-readers-lilac
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- lilac
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_lilac_reader.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-linear
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- linear
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_linear.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-llama-parse
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- llama_parse
|   |   |   |   |   |           \-- __init__.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-macrometa-gdn
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- macrometa_gdn
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_macrometa_gdn.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-make-com
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- make_com
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_make_com.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-mangadex
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- mangadex
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_mangadex.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-mangoapps-guides
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- mangoapps_guides
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_mangoapps_guides.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-maps
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- maps
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_maps.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-markitdown
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- markitdown
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_markitdownreader.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- MAKEFILE
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-mbox
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- mbox
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_mbox.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-memos
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- memos
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_memos.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-metal
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- metal
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_metal.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-microsoft-onedrive
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- microsoft_onedrive
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_microsoft_onedrive.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-microsoft-outlook
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- microsoft_outlook
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_outlook_localcalendar.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-microsoft-outlook-emails
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- microsoft_outlook_emails
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_microsoft_outlook_mails.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-microsoft-sharepoint
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- microsoft_sharepoint
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           |-- event.py
|   |   |   |   |   |           \-- file_path_info.png
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_microsoft_sharepoint.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-milvus
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- milvus
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_milvus.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-minio
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- readers
|   |   |   |   |   |   |   \-- minio
|   |   |   |   |   |   |       |-- boto3_client
|   |   |   |   |   |   |       |   |-- __init__.py
|   |   |   |   |   |   |       |   \-- base.py
|   |   |   |   |   |   |       |-- minio_client
|   |   |   |   |   |   |       |   |-- __init__.py
|   |   |   |   |   |   |       |   \-- base.py
|   |   |   |   |   |   |       \-- __init__.py
|   |   |   |   |   |   \-- README.md
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_minio.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-mondaydotcom
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- mondaydotcom
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_mondaydotcom.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-mongodb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- mongodb
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_mongo.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-myscale
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- myscale
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_myscale.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-notion
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- notion
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_notion.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-nougat-ocr
|   |   |   |   |   |-- examples
|   |   |   |   |   |   |-- mathpaper.pdf
|   |   |   |   |   |   \-- NougatOCR.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- nougat_ocr
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_nougat_ocr.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-obsidian
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- obsidian
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_obsidian.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-openalex
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- demo.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- openalex
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_openalex.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-opendal
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- opendal
|   |   |   |   |   |           |-- azblob
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           |-- gcs
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           |-- s3
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_opendal_reader.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-opensearch
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- opensearch
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_opensearch.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-oracleai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- oracleai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_oracleai.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-oxylabs
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- oxylabs
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- amazon_bestsellers.py
|   |   |   |   |   |           |-- amazon_pricing.py
|   |   |   |   |   |           |-- amazon_product.py
|   |   |   |   |   |           |-- amazon_reviews.py
|   |   |   |   |   |           |-- amazon_search.py
|   |   |   |   |   |           |-- amazon_sellers.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           |-- BUILD
|   |   |   |   |   |           |-- google_ads.py
|   |   |   |   |   |           |-- google_base.py
|   |   |   |   |   |           |-- google_search.py
|   |   |   |   |   |           |-- utils.py
|   |   |   |   |   |           \-- youtube_transcripts.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- BUILD
|   |   |   |   |   |   \-- test_readers_oxylabs.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-paddle-ocr
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- paddle_ocr
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_paddle_ocr.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-pandas-ai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- pandas_ai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-papers
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- papers
|   |   |   |   |   |           |-- arxiv
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           |-- pubmed
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           \-- __init__.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_papers.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-patentsview
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- patentsview
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_patentsview.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-pathway
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- pathway
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_pathway.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-pdb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- pdb
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_pdb.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-pdf-marker
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- pdf_marker
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-pdf-table
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- pdf_table
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_pdf_table.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-pebblo
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- pebblo
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utility.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_pebblo.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-preprocess
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- preprocess
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_preprocess.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-psychic
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- psychic
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_psychic.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-qdrant
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- qdrant
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_qdrant.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-quip
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- quip
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_quip.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-rayyan
|   |   |   |   |   |-- examples
|   |   |   |   |   |   |-- notebook-requirements.txt
|   |   |   |   |   |   \-- rayyan-loader.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- rayyan
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_rayyan.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-readwise
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- readwise
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_readwise.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-reddit
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- reddit
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_reddit.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-remote
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- remote
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_remote.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-remote-depth
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- remote_depth
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_remote_depth.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-s3
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- s3
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_s3.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-screenpipe
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- screenpipe
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_screenpipe.py
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   \-- README.md
|   |   |   |   |-- llama-index-readers-sec-filings
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- sec_filings
|   |   |   |   |   |           |-- prepline_sec_filings
|   |   |   |   |   |           |   |-- api
|   |   |   |   |   |           |   |   |-- __init__.py
|   |   |   |   |   |           |   |   |-- app.py
|   |   |   |   |   |           |   |   \-- section.py
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- fetch.py
|   |   |   |   |   |           |   |-- sec_document.py
|   |   |   |   |   |           |   \-- sections.py
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           |-- sec_filings.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_sec_filings.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-semanticscholar
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- demo_s2.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- semanticscholar
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test.py
|   |   |   |   |   |   \-- test_readers_semanticscholar.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-service-now
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- readers
|   |   |   |   |   |   |   |-- service_now
|   |   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |   |-- base.py
|   |   |   |   |   |   |   |   \-- event.py
|   |   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |   \-- __init__.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_snow_kb_reader.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-singlestore
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- singlestore
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_singlestore.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-slack
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- slack
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_slack.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-smart-pdf-loader
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- smart_pdf_loader
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-snowflake
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- snowflake
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_snowflake.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-solr
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- solr
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_solr.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-spotify
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- spotify
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_spotify.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-stackoverflow
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- stackoverflow
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_stackoverflow.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-steamship
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- steamship
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_steamship.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-string-iterable
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- string_iterable
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_string_iterable.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-stripe-docs
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- stripe_docs
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-structured-data
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- structured_data
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_structured_data.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-telegram
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- telegram
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_telegram.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-toggl
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- toggl
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- dto.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-trello
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- trello
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_trello.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-twitter
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- twitter
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_twitter.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-txtai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- txtai
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_txtai.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-uniprot
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- uniprot
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   \-- test_uniprot_reader.py
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-upstage
|   |   |   |   |   |-- examples
|   |   |   |   |   |   |-- UpstageDocumentParseReader.ipynb
|   |   |   |   |   |   \-- UpstageLayoutAnalysisReader.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- upstage
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- document_parse.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_upstage.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-weather
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- weather
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_weather.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-weaviate
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- weaviate
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_weaviate.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-web
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- web
|   |   |   |   |   |           |-- agentql_web
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   \-- README.md
|   |   |   |   |   |           |-- async_web
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   \-- README.md
|   |   |   |   |   |           |-- beautiful_soup_web
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   |-- README.md
|   |   |   |   |   |           |   \-- requirements.txt
|   |   |   |   |   |           |-- browserbase_web
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   |-- README.md
|   |   |   |   |   |           |   \-- requirements.txt
|   |   |   |   |   |           |-- firecrawl_web
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   |-- README.md
|   |   |   |   |   |           |   \-- requirements.txt
|   |   |   |   |   |           |-- hyperbrowser_web
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   |-- README.md
|   |   |   |   |   |           |   \-- requirements.txt
|   |   |   |   |   |           |-- knowledge_base
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   |-- README.md
|   |   |   |   |   |           |   \-- requirements.txt
|   |   |   |   |   |           |-- main_content_extractor
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   |-- README.md
|   |   |   |   |   |           |   \-- requirements.txt
|   |   |   |   |   |           |-- news
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   |-- README.md
|   |   |   |   |   |           |   \-- requirements.txt
|   |   |   |   |   |           |-- olostep_web
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   |-- README.md
|   |   |   |   |   |           |   \-- requirements.txt
|   |   |   |   |   |           |-- oxylabs_web
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   |-- BUILD
|   |   |   |   |   |           |   |-- README.md
|   |   |   |   |   |           |   |-- requirements.txt
|   |   |   |   |   |           |   \-- utils.py
|   |   |   |   |   |           |-- readability_web
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   |-- Readability.js
|   |   |   |   |   |           |   |-- README.md
|   |   |   |   |   |           |   \-- requirements.txt
|   |   |   |   |   |           |-- rss
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   \-- README.md
|   |   |   |   |   |           |-- rss_news
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   |-- README.md
|   |   |   |   |   |           |   \-- sample_rss_feeds.opml
|   |   |   |   |   |           |-- scrapfly_web
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   |-- README.md
|   |   |   |   |   |           |   \-- requirements.txt
|   |   |   |   |   |           |-- scrapy_web
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   |-- README.md
|   |   |   |   |   |           |   |-- requirements.txt
|   |   |   |   |   |           |   \-- utils.py
|   |   |   |   |   |           |-- simple_web
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   |-- README.md
|   |   |   |   |   |           |   \-- requirements.txt
|   |   |   |   |   |           |-- sitemap
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   |-- README.md
|   |   |   |   |   |           |   \-- requirements.txt
|   |   |   |   |   |           |-- spider_web
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   |-- README.md
|   |   |   |   |   |           |   \-- requirements.txt
|   |   |   |   |   |           |-- trafilatura_web
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   |-- README.md
|   |   |   |   |   |           |   \-- requirements.txt
|   |   |   |   |   |           |-- unstructured_web
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   |-- README.md
|   |   |   |   |   |           |   \-- requirements.txt
|   |   |   |   |   |           |-- whole_site
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   |-- README.md
|   |   |   |   |   |           |   \-- requirements.txt
|   |   |   |   |   |           |-- zenrows_web
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   \-- README.md
|   |   |   |   |   |           |-- zyte_web
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   |-- README.md
|   |   |   |   |   |           |   \-- requirements.txt
|   |   |   |   |   |           \-- __init__.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_async_web.py
|   |   |   |   |   |   |-- test_firecrawl_requests.py
|   |   |   |   |   |   |-- test_firecrawl_web_reader.py
|   |   |   |   |   |   |-- test_readers_oxylabs.py
|   |   |   |   |   |   |-- test_readers_rss.py
|   |   |   |   |   |   |-- test_scrapy_web_reader.py
|   |   |   |   |   |   |-- test_simple_webreader.py
|   |   |   |   |   |   \-- test_zenrows_web.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-whatsapp
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- whatsapp
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_whatsapp.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-whisper
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- whisper
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   \-- test_readers_whisper.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- test_audio.mp3
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-wikipedia
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- wikipedia
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_wikipedia.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-wordlift
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- wordlift
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_wordlift.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-wordpress
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- wordpress
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_wordpress.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-youtube-transcript
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- youtube_transcript
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_youtube_transcript.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-zendesk
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- zendesk
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_zendesk.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-zep
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- zep
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_zep.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-zulip
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- zulip
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_zulip.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-readers-zyte-serp
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- readers
|   |   |   |   |   |       \-- zyte_serp
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_readers_zyte_serp.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   \-- README.md
|   |   |   |-- response_synthesizers
|   |   |   |   \-- llama-index-response-synthesizers-google
|   |   |   |       |-- llama_index
|   |   |   |       |   \-- response_synthesizers
|   |   |   |       |       \-- google
|   |   |   |       |           |-- __init__.py
|   |   |   |       |           \-- base.py
|   |   |   |       |-- tests
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   \-- test_response_synthesizers_google.py
|   |   |   |       |-- .gitignore
|   |   |   |       |-- LICENSE
|   |   |   |       |-- Makefile
|   |   |   |       |-- pyproject.toml
|   |   |   |       |-- README.md
|   |   |   |       \-- uv.lock
|   |   |   |-- retrievers
|   |   |   |   |-- llama-index-retrievers-alletra-x10000
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- retrievers
|   |   |   |   |   |       \-- alletra_x10000_retriever
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-retrievers-bedrock
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- retrievers
|   |   |   |   |   |       \-- bedrock
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_retrievers_bedrock.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-retrievers-bm25
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- retrievers
|   |   |   |   |   |       \-- bm25
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_retrievers_bm25_retriever.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-retrievers-duckdb-retriever
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- retrievers
|   |   |   |   |   |       \-- duckdb_retriever
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_retrievers_bm25_retriever.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-retrievers-galaxia
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- example_1.py
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- retrievers
|   |   |   |   |   |       \-- galaxia
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_retrievers_galaxia.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-retrievers-kendra
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- retrievers
|   |   |   |   |   |       \-- kendra
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_retrievers_kendra.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-retrievers-mongodb-atlas-bm25-retriever
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- retrievers
|   |   |   |   |   |       \-- mongodb_atlas_bm25_retriever
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_retrievers_bm25_retriever.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-retrievers-pathway
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- retrievers
|   |   |   |   |   |       \-- pathway
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_retrievers_pathway_retriever.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-retrievers-superlinked
|   |   |   |   |   |-- examples
|   |   |   |   |   |   |-- steam_games_example.ipynb
|   |   |   |   |   |   \-- steam_games_example.py
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- retrievers
|   |   |   |   |   |       \-- superlinked
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- retriever.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- test_integration_superlinked_retriever.py
|   |   |   |   |   |   \-- test_unit_superlinked_retriever.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-retrievers-tldw
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- retrievers
|   |   |   |   |   |       \-- tldw
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_retrievers_tldw_retriever.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-retrievers-vectorize
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- retrievers
|   |   |   |   |   |       \-- vectorize
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- research.pdf
|   |   |   |   |   |   \-- test_retrievers_vectorize.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-retrievers-vertexai-search
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- retrievers
|   |   |   |   |   |       \-- vertexai_search
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- _utils.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_retrievers_vertexai_search.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-retrievers-videodb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- retrievers
|   |   |   |   |   |       \-- videodb
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_retrievers_videdb.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- MAKEFILE
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   \-- llama-index-retrievers-you
|   |   |   |       |-- llama_index
|   |   |   |       |   \-- retrievers
|   |   |   |       |       \-- you
|   |   |   |       |           |-- __init__.py
|   |   |   |       |           \-- base.py
|   |   |   |       |-- tests
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   \-- test_retrievers_you_retriever.py
|   |   |   |       |-- .gitignore
|   |   |   |       |-- LICENSE
|   |   |   |       |-- Makefile
|   |   |   |       |-- pyproject.toml
|   |   |   |       |-- README.md
|   |   |   |       \-- uv.lock
|   |   |   |-- selectors
|   |   |   |   \-- llama-index-selectors-notdiamond
|   |   |   |       |-- llama_index
|   |   |   |       |   \-- selectors
|   |   |   |       |       \-- notdiamond
|   |   |   |       |           |-- __init__.py
|   |   |   |       |           \-- base.py
|   |   |   |       |-- .gitignore
|   |   |   |       |-- LICENSE
|   |   |   |       |-- Makefile
|   |   |   |       |-- pyproject.toml
|   |   |   |       |-- README.md
|   |   |   |       \-- uv.lock
|   |   |   |-- sparse_embeddings
|   |   |   |   \-- llama-index-sparse-embeddings-fastembed
|   |   |   |       |-- llama_index
|   |   |   |       |   \-- sparse_embeddings
|   |   |   |       |       \-- fastembed
|   |   |   |       |           |-- __init__.py
|   |   |   |       |           \-- base.py
|   |   |   |       |-- tests
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- conftest.py
|   |   |   |       |   \-- test_sparse_embeddings_fastembed.py
|   |   |   |       |-- LICENSE
|   |   |   |       |-- Makefile
|   |   |   |       |-- pyproject.toml
|   |   |   |       |-- README.md
|   |   |   |       \-- uv.lock
|   |   |   |-- storage
|   |   |   |   |-- chat_store
|   |   |   |   |   |-- llama-index-storage-chat-store-azure
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- chat_store
|   |   |   |   |   |   |           \-- azure
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_chat_store_azure_chat_store.py
|   |   |   |   |   |   |-- .gitignore
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-chat-store-azurecosmosmongovcore
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- chat_store
|   |   |   |   |   |   |           \-- azurecosmosmongovcore
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_storage_azurecosmosmongovcore_chat_store.py
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-chat-store-azurecosmosnosql
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- chat_store
|   |   |   |   |   |   |           \-- azurecosmosnosql
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_storage_azurecosmosnosql_chat_store.py
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-chat-store-dynamodb
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- chat_store
|   |   |   |   |   |   |           \-- dynamodb
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_chat_store_dynamodb_chat_store.py
|   |   |   |   |   |   |-- .gitignore
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-chat-store-gel
|   |   |   |   |   |   |-- dbschema
|   |   |   |   |   |   |   |-- migrations
|   |   |   |   |   |   |   |   \-- 00001-m1ze2pu.edgeql
|   |   |   |   |   |   |   |-- default.gel
|   |   |   |   |   |   |   \-- scoping.gel
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- chat_store
|   |   |   |   |   |   |           \-- gel
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_chat_store_gel_chat_store.py
|   |   |   |   |   |   |-- .gitignore
|   |   |   |   |   |   |-- gel.toml
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-chat-store-mongo
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- chat_store
|   |   |   |   |   |   |           \-- mongo
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |   \-- test_chat_store_mongo_chat_store.py
|   |   |   |   |   |   |-- .gitignore
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-chat-store-opensearch
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- chat_store
|   |   |   |   |   |   |           \-- opensearch
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_opensearch_chat_store.py
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-chat-store-postgres
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- chat_store
|   |   |   |   |   |   |           \-- postgres
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |   \-- test_chat_store_postgres_chat_store.py
|   |   |   |   |   |   |-- .gitignore
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-chat-store-redis
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- chat_store
|   |   |   |   |   |   |           \-- redis
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_chat_store_redis_chat_store.py
|   |   |   |   |   |   |-- .gitignore
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-chat-store-sqlite
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- chat_store
|   |   |   |   |   |   |           \-- sqlite
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |   \-- test_chat_store_sqlite_chat_store.py
|   |   |   |   |   |   |-- .gitignore
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-chat-store-tablestore
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- chat_store
|   |   |   |   |   |   |           \-- tablestore
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_chat_store_tablestore_chat_store.py
|   |   |   |   |   |   |-- .gitignore
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-chat-store-upstash
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- chat_store
|   |   |   |   |   |   |           \-- upstash
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |   \-- test_chat_store_upstash_chat_store.py
|   |   |   |   |   |   |-- .gitignore
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   \-- llama-index-storage-chat-store-yugabytedb
|   |   |   |   |       |-- llama_index
|   |   |   |   |       |   \-- storage
|   |   |   |   |       |       \-- chat_store
|   |   |   |   |       |           \-- yugabytedb
|   |   |   |   |       |               |-- __init__.py
|   |   |   |   |       |               \-- base.py
|   |   |   |   |       |-- tests
|   |   |   |   |       |   |-- __init__.py
|   |   |   |   |       |   |-- conftest.py
|   |   |   |   |       |   \-- test_chat_store_yugabytedb_chat_store.py
|   |   |   |   |       |-- .gitignore
|   |   |   |   |       |-- LICENSE
|   |   |   |   |       |-- Makefile
|   |   |   |   |       |-- pyproject.toml
|   |   |   |   |       |-- README.md
|   |   |   |   |       \-- uv.lock
|   |   |   |   |-- docstore
|   |   |   |   |   |-- llama-index-storage-docstore-azure
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- docstore
|   |   |   |   |   |   |           \-- azure
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_storage_docstore_azure.py
|   |   |   |   |   |   |-- .gitignore
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-docstore-azurecosmosnosql
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- docstore
|   |   |   |   |   |   |           \-- azurecosmosnosql
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_storage_document_store_azurecosmosnosql.py
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-docstore-couchbase
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- docstore
|   |   |   |   |   |   |           \-- couchbase
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_docstore_couchbase.py
|   |   |   |   |   |   |-- .gitignore
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-docstore-duckdb
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- docstore
|   |   |   |   |   |   |           \-- duckdb
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_storage_docstore_duckdb.py
|   |   |   |   |   |   |-- .gitignore
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-docstore-dynamodb
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- docstore
|   |   |   |   |   |   |           \-- dynamodb
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_storage_docstore_dynamodb.py
|   |   |   |   |   |   |-- .gitignore
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-docstore-elasticsearch
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- docstore
|   |   |   |   |   |   |           \-- elasticsearch
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_storage_docstore_elasticsearch.py
|   |   |   |   |   |   |-- .gitignore
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-docstore-firestore
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- docstore
|   |   |   |   |   |   |           \-- firestore
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_storage_docstore_firestore.py
|   |   |   |   |   |   |-- .gitignore
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-docstore-gel
|   |   |   |   |   |   |-- dbschema
|   |   |   |   |   |   |   |-- migrations
|   |   |   |   |   |   |   |   \-- 00001-m1mnp6b.edgeql
|   |   |   |   |   |   |   |-- default.gel
|   |   |   |   |   |   |   \-- scoping.gel
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- docstore
|   |   |   |   |   |   |           \-- gel
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_gel.py
|   |   |   |   |   |   |   \-- test_storage_docstore_gel.py
|   |   |   |   |   |   |-- .gitignore
|   |   |   |   |   |   |-- gel.toml
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-docstore-mongodb
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- docstore
|   |   |   |   |   |   |           \-- mongodb
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_storage_docstore_mongodb.py
|   |   |   |   |   |   |-- .gitignore
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-docstore-postgres
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- docstore
|   |   |   |   |   |   |           \-- postgres
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- .gitignore
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-docstore-redis
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- docstore
|   |   |   |   |   |   |           \-- redis
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_storage_docstore_redis.py
|   |   |   |   |   |   |-- .gitignore
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   \-- llama-index-storage-docstore-tablestore
|   |   |   |   |       |-- llama_index
|   |   |   |   |       |   \-- storage
|   |   |   |   |       |       \-- docstore
|   |   |   |   |       |           \-- tablestore
|   |   |   |   |       |               |-- __init__.py
|   |   |   |   |       |               \-- base.py
|   |   |   |   |       |-- tests
|   |   |   |   |       |   |-- __init__.py
|   |   |   |   |       |   \-- test_storage_docstore_tablestore.py
|   |   |   |   |       |-- .gitignore
|   |   |   |   |       |-- LICENSE
|   |   |   |   |       |-- Makefile
|   |   |   |   |       |-- pyproject.toml
|   |   |   |   |       |-- README.md
|   |   |   |   |       \-- uv.lock
|   |   |   |   |-- index_store
|   |   |   |   |   |-- llama-index-storage-index-store-azure
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- index_store
|   |   |   |   |   |   |           \-- azure
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_storage_index_store_azure.py
|   |   |   |   |   |   |-- .gitignore
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-index-store-azurecosmosnosql
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- index_store
|   |   |   |   |   |   |           \-- azurecosmosnosql
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_storage_index_store_azurecosmosnosql.py
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-index-store-couchbase
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- index_store
|   |   |   |   |   |   |           \-- couchbase
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_index_store_couchbase.py
|   |   |   |   |   |   |-- .gitignore
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-index-store-duckdb
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- index_store
|   |   |   |   |   |   |           \-- duckdb
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_storage_index_store_duckdb.py
|   |   |   |   |   |   |-- .gitignore
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-index-store-dynamodb
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- index_store
|   |   |   |   |   |   |           \-- dynamodb
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_storage_index_store_dynamodb.py
|   |   |   |   |   |   |-- .gitignore
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-index-store-elasticsearch
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- index_store
|   |   |   |   |   |   |           \-- elasticsearch
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_storage_index_store_elasticsearch.py
|   |   |   |   |   |   |-- .gitignore
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-index-store-firestore
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- index_store
|   |   |   |   |   |   |           \-- firestore
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_storage_index_store_firestore.py
|   |   |   |   |   |   |-- .gitignore
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-index-store-gel
|   |   |   |   |   |   |-- dbschema
|   |   |   |   |   |   |   |-- migrations
|   |   |   |   |   |   |   |   \-- 00001-m1mnp6b.edgeql
|   |   |   |   |   |   |   |-- default.gel
|   |   |   |   |   |   |   \-- scoping.gel
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- index_store
|   |   |   |   |   |   |           \-- gel
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_gel.py
|   |   |   |   |   |   |   \-- test_storage_index_store_gel.py
|   |   |   |   |   |   |-- .gitignore
|   |   |   |   |   |   |-- gel.toml
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-index-store-mongodb
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- index_store
|   |   |   |   |   |   |           \-- mongodb
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_storage_index_store_mongodb.py
|   |   |   |   |   |   |-- .gitignore
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-index-store-postgres
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- index_store
|   |   |   |   |   |   |           \-- postgres
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_storage_index_store_postgres.py
|   |   |   |   |   |   |-- .gitignore
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   |-- llama-index-storage-index-store-redis
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   \-- storage
|   |   |   |   |   |   |       \-- index_store
|   |   |   |   |   |   |           \-- redis
|   |   |   |   |   |   |               |-- __init__.py
|   |   |   |   |   |   |               \-- base.py
|   |   |   |   |   |   |-- tests
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   \-- test_storage_index_store_redis.py
|   |   |   |   |   |   |-- .gitignore
|   |   |   |   |   |   |-- LICENSE
|   |   |   |   |   |   |-- Makefile
|   |   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   \-- uv.lock
|   |   |   |   |   \-- llama-index-storage-index-store-tablestore
|   |   |   |   |       |-- llama_index
|   |   |   |   |       |   \-- storage
|   |   |   |   |       |       \-- index_store
|   |   |   |   |       |           \-- tablestore
|   |   |   |   |       |               |-- __init__.py
|   |   |   |   |       |               \-- base.py
|   |   |   |   |       |-- tests
|   |   |   |   |       |   |-- __init__.py
|   |   |   |   |       |   \-- test_storage_index_store_tablestore.py
|   |   |   |   |       |-- .gitignore
|   |   |   |   |       |-- LICENSE
|   |   |   |   |       |-- Makefile
|   |   |   |   |       |-- pyproject.toml
|   |   |   |   |       |-- README.md
|   |   |   |   |       \-- uv.lock
|   |   |   |   \-- kvstore
|   |   |   |       |-- llama-index-storage-kvstore-azure
|   |   |   |       |   |-- llama_index
|   |   |   |       |   |   \-- storage
|   |   |   |       |   |       \-- kvstore
|   |   |   |       |   |           \-- azure
|   |   |   |       |   |               |-- __init__.py
|   |   |   |       |   |               \-- base.py
|   |   |   |       |   |-- tests
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   \-- test_storage_kvstore_azure.py
|   |   |   |       |   |-- .gitignore
|   |   |   |       |   |-- LICENSE
|   |   |   |       |   |-- Makefile
|   |   |   |       |   |-- pyproject.toml
|   |   |   |       |   |-- README.md
|   |   |   |       |   \-- uv.lock
|   |   |   |       |-- llama-index-storage-kvstore-azurecosmosnosql
|   |   |   |       |   |-- llama_index
|   |   |   |       |   |   \-- storage
|   |   |   |       |   |       \-- kvstore
|   |   |   |       |   |           \-- azurecosmosnosql
|   |   |   |       |   |               |-- __init__.py
|   |   |   |       |   |               \-- base.py
|   |   |   |       |   |-- tests
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   \-- test_storage_azurecosmosnosql_kv_store.py
|   |   |   |       |   |-- LICENSE
|   |   |   |       |   |-- Makefile
|   |   |   |       |   |-- pyproject.toml
|   |   |   |       |   |-- README.md
|   |   |   |       |   \-- uv.lock
|   |   |   |       |-- llama-index-storage-kvstore-couchbase
|   |   |   |       |   |-- llama_index
|   |   |   |       |   |   \-- storage
|   |   |   |       |   |       \-- kvstore
|   |   |   |       |   |           \-- couchbase
|   |   |   |       |   |               |-- __init__.py
|   |   |   |       |   |               \-- base.py
|   |   |   |       |   |-- tests
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   \-- test_kvstore_couchbase.py
|   |   |   |       |   |-- .gitignore
|   |   |   |       |   |-- LICENSE
|   |   |   |       |   |-- Makefile
|   |   |   |       |   |-- pyproject.toml
|   |   |   |       |   |-- README.md
|   |   |   |       |   \-- uv.lock
|   |   |   |       |-- llama-index-storage-kvstore-duckdb
|   |   |   |       |   |-- llama_index
|   |   |   |       |   |   \-- storage
|   |   |   |       |   |       \-- kvstore
|   |   |   |       |   |           \-- duckdb
|   |   |   |       |   |               |-- __init__.py
|   |   |   |       |   |               \-- base.py
|   |   |   |       |   |-- tests
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   \-- test_storage_kvstore_duckdb.py
|   |   |   |       |   |-- .gitignore
|   |   |   |       |   |-- LICENSE
|   |   |   |       |   |-- Makefile
|   |   |   |       |   |-- pyproject.toml
|   |   |   |       |   |-- README.md
|   |   |   |       |   \-- uv.lock
|   |   |   |       |-- llama-index-storage-kvstore-dynamodb
|   |   |   |       |   |-- llama_index
|   |   |   |       |   |   \-- storage
|   |   |   |       |   |       \-- kvstore
|   |   |   |       |   |           \-- dynamodb
|   |   |   |       |   |               |-- __init__.py
|   |   |   |       |   |               \-- base.py
|   |   |   |       |   |-- tests
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   \-- test_storage_kvstore_dynamodb.py
|   |   |   |       |   |-- .gitignore
|   |   |   |       |   |-- LICENSE
|   |   |   |       |   |-- Makefile
|   |   |   |       |   |-- pyproject.toml
|   |   |   |       |   |-- README.md
|   |   |   |       |   \-- uv.lock
|   |   |   |       |-- llama-index-storage-kvstore-elasticsearch
|   |   |   |       |   |-- llama_index
|   |   |   |       |   |   \-- storage
|   |   |   |       |   |       \-- kvstore
|   |   |   |       |   |           \-- elasticsearch
|   |   |   |       |   |               |-- __init__.py
|   |   |   |       |   |               \-- base.py
|   |   |   |       |   |-- tests
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   \-- test_storage_kvstore_elasticsearch.py
|   |   |   |       |   |-- .gitignore
|   |   |   |       |   |-- LICENSE
|   |   |   |       |   |-- Makefile
|   |   |   |       |   |-- pyproject.toml
|   |   |   |       |   |-- README.md
|   |   |   |       |   \-- uv.lock
|   |   |   |       |-- llama-index-storage-kvstore-firestore
|   |   |   |       |   |-- llama_index
|   |   |   |       |   |   \-- storage
|   |   |   |       |   |       \-- kvstore
|   |   |   |       |   |           \-- firestore
|   |   |   |       |   |               |-- __init__.py
|   |   |   |       |   |               \-- base.py
|   |   |   |       |   |-- tests
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   \-- test_storage_kvstore_firestore.py
|   |   |   |       |   |-- .gitignore
|   |   |   |       |   |-- LICENSE
|   |   |   |       |   |-- Makefile
|   |   |   |       |   |-- pyproject.toml
|   |   |   |       |   |-- README.md
|   |   |   |       |   \-- uv.lock
|   |   |   |       |-- llama-index-storage-kvstore-gel
|   |   |   |       |   |-- dbschema
|   |   |   |       |   |   |-- migrations
|   |   |   |       |   |   |   |-- 00001-m1qleqa.edgeql
|   |   |   |       |   |   |   |-- 00002-m14juxo.edgeql
|   |   |   |       |   |   |   |-- 00003-m1lr5dv.edgeql
|   |   |   |       |   |   |   |-- 00004-m17iwsk.edgeql
|   |   |   |       |   |   |   \-- 00005-m1vdsze.edgeql
|   |   |   |       |   |   |-- default.gel
|   |   |   |       |   |   \-- scoping.gel
|   |   |   |       |   |-- llama_index
|   |   |   |       |   |   \-- storage
|   |   |   |       |   |       \-- kvstore
|   |   |   |       |   |           \-- gel
|   |   |   |       |   |               |-- __init__.py
|   |   |   |       |   |               \-- base.py
|   |   |   |       |   |-- tests
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- test_gel.py
|   |   |   |       |   |   \-- test_storage_kvstore_gel.py
|   |   |   |       |   |-- .gitignore
|   |   |   |       |   |-- gel.toml
|   |   |   |       |   |-- LICENSE
|   |   |   |       |   |-- Makefile
|   |   |   |       |   |-- pyproject.toml
|   |   |   |       |   |-- README.md
|   |   |   |       |   \-- uv.lock
|   |   |   |       |-- llama-index-storage-kvstore-mongodb
|   |   |   |       |   |-- llama_index
|   |   |   |       |   |   \-- storage
|   |   |   |       |   |       \-- kvstore
|   |   |   |       |   |           \-- mongodb
|   |   |   |       |   |               |-- __init__.py
|   |   |   |       |   |               \-- base.py
|   |   |   |       |   |-- tests
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   \-- test_storage_kvstore_mongodb.py
|   |   |   |       |   |-- .gitignore
|   |   |   |       |   |-- LICENSE
|   |   |   |       |   |-- Makefile
|   |   |   |       |   |-- pyproject.toml
|   |   |   |       |   |-- README.md
|   |   |   |       |   \-- uv.lock
|   |   |   |       |-- llama-index-storage-kvstore-postgres
|   |   |   |       |   |-- llama_index
|   |   |   |       |   |   \-- storage
|   |   |   |       |   |       \-- kvstore
|   |   |   |       |   |           \-- postgres
|   |   |   |       |   |               |-- __init__.py
|   |   |   |       |   |               \-- base.py
|   |   |   |       |   |-- tests
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   |-- conftest.py
|   |   |   |       |   |   |-- test_postgres.py
|   |   |   |       |   |   \-- test_storage_kvstore_postgres.py
|   |   |   |       |   |-- .gitignore
|   |   |   |       |   |-- LICENSE
|   |   |   |       |   |-- Makefile
|   |   |   |       |   |-- pyproject.toml
|   |   |   |       |   |-- README.md
|   |   |   |       |   \-- uv.lock
|   |   |   |       |-- llama-index-storage-kvstore-redis
|   |   |   |       |   |-- llama_index
|   |   |   |       |   |   \-- storage
|   |   |   |       |   |       \-- kvstore
|   |   |   |       |   |           \-- redis
|   |   |   |       |   |               |-- __init__.py
|   |   |   |       |   |               \-- base.py
|   |   |   |       |   |-- tests
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   \-- test_storage_kvstore_redis.py
|   |   |   |       |   |-- .gitignore
|   |   |   |       |   |-- LICENSE
|   |   |   |       |   |-- Makefile
|   |   |   |       |   |-- pyproject.toml
|   |   |   |       |   |-- README.md
|   |   |   |       |   \-- uv.lock
|   |   |   |       |-- llama-index-storage-kvstore-s3
|   |   |   |       |   |-- llama_index
|   |   |   |       |   |   \-- storage
|   |   |   |       |   |       \-- kvstore
|   |   |   |       |   |           \-- s3
|   |   |   |       |   |               |-- __init__.py
|   |   |   |       |   |               \-- base.py
|   |   |   |       |   |-- tests
|   |   |   |       |   |   |-- __init__.py
|   |   |   |       |   |   \-- test_store_kvstore_s3.py
|   |   |   |       |   |-- .gitignore
|   |   |   |       |   |-- LICENSE
|   |   |   |       |   |-- Makefile
|   |   |   |       |   |-- pyproject.toml
|   |   |   |       |   |-- README.md
|   |   |   |       |   \-- uv.lock
|   |   |   |       \-- llama-index-storage-kvstore-tablestore
|   |   |   |           |-- llama_index
|   |   |   |           |   \-- storage
|   |   |   |           |       \-- kvstore
|   |   |   |           |           \-- tablestore
|   |   |   |           |               |-- __init__.py
|   |   |   |           |               \-- base.py
|   |   |   |           |-- tests
|   |   |   |           |   |-- __init__.py
|   |   |   |           |   \-- test_storage_kvstore_tablestore.py
|   |   |   |           |-- .gitignore
|   |   |   |           |-- LICENSE
|   |   |   |           |-- Makefile
|   |   |   |           |-- pyproject.toml
|   |   |   |           |-- README.md
|   |   |   |           \-- uv.lock
|   |   |   |-- tools
|   |   |   |   |-- llama-index-tools-agentql
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- AgentQL_browser_agent.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- agentql
|   |   |   |   |   |           |-- agentql_browser_tool
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           |-- agentql_rest_api_tool
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- const.py
|   |   |   |   |   |           |-- messages.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_browser_spec.py
|   |   |   |   |   |   \-- test_rest_api_spec.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-airweave
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- airweave_search.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- airweave
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_airweave.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-artifact-editor
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- artifact_editor
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- memory_block.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   \-- test_artifact_editor.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-arxiv
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- arxiv.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- arxiv
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_arxiv.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-aws-bedrock-agentcore
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- aws_bedrock_agentcore
|   |   |   |   |   |           |-- browser
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- base.py
|   |   |   |   |   |           |   |-- browser_session_manager.py
|   |   |   |   |   |           |   \-- utils.py
|   |   |   |   |   |           |-- code_interpreter
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           \-- __init__.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_browser.py
|   |   |   |   |   |   |-- test_browser_async.py
|   |   |   |   |   |   |-- test_browser_session_manager.py
|   |   |   |   |   |   |-- test_browser_spec.py
|   |   |   |   |   |   |-- test_browser_utils.py
|   |   |   |   |   |   |-- test_code_interpreter.py
|   |   |   |   |   |   \-- test_code_interpreter_spec.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-azure-code-interpreter
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- azure_code_interpreter
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_azure_aca_session.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-azure-cv
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- azure_vision.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- azure_cv
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_azure_cv.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-azure-speech
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- azure_speech.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- azure_speech
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_azure_speech.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-azure-translate
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- azure_translate
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_azure_translate.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-bing-search
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- bing_search.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- bing_search
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_bing_search.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-box
|   |   |   |   |   |-- examples
|   |   |   |   |   |   |-- box_ai_extract.ipynb
|   |   |   |   |   |   |-- box_ai_prompt.ipynb
|   |   |   |   |   |   |-- box_extract.ipynb
|   |   |   |   |   |   |-- box_search.ipynb
|   |   |   |   |   |   \-- box_search_by_metadata.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- box
|   |   |   |   |   |           |-- ai_extract
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           |-- ai_prompt
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           |-- search
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           |-- search_by_metadata
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           |-- text_extract
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           \-- __init__.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_tools_box.py
|   |   |   |   |   |   |-- test_tools_box_ai_extract.py
|   |   |   |   |   |   |-- test_tools_box_ai_prompt.py
|   |   |   |   |   |   |-- test_tools_box_search.py
|   |   |   |   |   |   |-- test_tools_box_search_by_metadata.py
|   |   |   |   |   |   \-- test_tools_box_text_extract.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-brave-search
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- brave_search.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- brave_search
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_brave_search.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-brightdata
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- brightdata
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_brightdata.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-cassandra
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- cassandra
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- cassandra_database_wrapper.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_cassandra.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-chatgpt-plugin
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- chatgpt_plugin.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- chatgpt_plugin
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_chatgpt_plugin.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-code-interpreter
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- code_interpreter.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- code_interpreter
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_code_interpreter.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-cogniswitch
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- cogniswitch.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- cogniswitch
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_cogniswitch.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-dappier
|   |   |   |   |   |-- examples
|   |   |   |   |   |   |-- dappier_ai_recommendations.ipynb
|   |   |   |   |   |   \-- dappier_real_time_search.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- dappier
|   |   |   |   |   |           |-- ai_recommendations
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           |-- real_time_search
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           \-- __init__.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_tools_dappier_ai_recommendations.py
|   |   |   |   |   |   \-- test_tools_dappier_real_time_search.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-database
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- database.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- database
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_database.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-desearch
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- desearch.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- desearch
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_desearch.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-duckduckgo
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- duckduckgo_search.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- duckduckgo
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_duckduckgo.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-elevenlabs
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- elevenlabs_speech.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- elevenlabs
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_elevenlabs.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-exa
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- exa.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- exa
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_exa.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-finance
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- finance_agent.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- finance
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           |-- comparisons.py
|   |   |   |   |   |           |-- earnings.py
|   |   |   |   |   |           |-- news.py
|   |   |   |   |   |           \-- util.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_finance_tools.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-google
|   |   |   |   |   |-- examples
|   |   |   |   |   |   |-- advanced_tools_usage.ipynb
|   |   |   |   |   |   |-- gmail.ipynb
|   |   |   |   |   |   |-- google_calendar.ipynb
|   |   |   |   |   |   \-- google_search.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- google
|   |   |   |   |   |           |-- calendar
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           |-- gmail
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           |-- search
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           \-- __init__.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_google.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-graphql
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- graphql.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- graphql
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_graphql.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-hive
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- hive_demo.py
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- hive
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- readme.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-igpt-email
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- igpt_email
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_igpt_email.py
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   \-- README.md
|   |   |   |   |-- llama-index-tools-ionic-shopping
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- ionic_shopping.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- ionic_shopping
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_ionic_shopping.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-jina
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- jina_search.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- jina
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_jina.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-jira
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- jira
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_jira.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-jira-issue
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- jira_issue
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_jira_issue.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-linkup-research
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- linkup.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- linkup_research
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_linkup_research.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-mcp
|   |   |   |   |   |-- examples
|   |   |   |   |   |   |-- .env.example
|   |   |   |   |   |   |-- mcp.ipynb
|   |   |   |   |   |   \-- mcp_server.py
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- mcp
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           |-- client.py
|   |   |   |   |   |           |-- tool_spec_mixins.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- schemas.py
|   |   |   |   |   |   |-- server.py
|   |   |   |   |   |   |-- test_client.py
|   |   |   |   |   |   \-- test_tools_mcp.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-mcp-discovery
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- basic_usage.py
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- mcp_discovery
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   \-- test_mcp_discovery.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-measurespace
|   |   |   |   |   |-- examples
|   |   |   |   |   |   |-- example.ipynb
|   |   |   |   |   |   \-- example.py
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- measurespace
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-metaphor
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- metaphor.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- metaphor
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_metaphor.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-moss
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- moss_agent.py
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- moss
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   \-- test_base.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-multion
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- multion.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- multion
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_multion.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-neo4j
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- neo4j
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- query_validator.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-notion
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- notion.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- notion
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_notion.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-openai
|   |   |   |   |   |-- examples
|   |   |   |   |   |   |-- multimodal_openai_image.ipynb
|   |   |   |   |   |   \-- openai_image_generation_agent.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- openai
|   |   |   |   |   |           |-- image_generation
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           \-- __init__.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_openai_image_generation.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-openapi
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- openapi_and_requests.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- openapi
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- example.json
|   |   |   |   |   |   \-- test_tools_openapi.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-parallel-web-systems
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- parallel_web_systems.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- parallel_web_systems
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_parallel_web_systems.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- requirements.txt
|   |   |   |   |-- llama-index-tools-playgrounds
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- playgrounds
|   |   |   |   |   |           |-- subgraph_connector
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           |-- subgraph_inspector
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   \-- base.py
|   |   |   |   |   |           \-- __init__.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_playgrounds.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-playwright
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- playwright_browser_agent.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- playwright
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_playwright.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-python-file
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- python_file
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_python_file.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-requests
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- requests
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_requests.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-salesforce
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- salesforce
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_salesforce.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-scrapegraph
|   |   |   |   |   |-- examples
|   |   |   |   |   |   |-- complete-scrapegraph-examples.py
|   |   |   |   |   |   |-- scrapegraph-agentic-scraper-llama-index.py
|   |   |   |   |   |   |-- scrapegraph-markdowinify-llama-index.py
|   |   |   |   |   |   |-- scrapegraph-scrape-llama-index.py
|   |   |   |   |   |   |-- scrapegraph-search-llama-index.py
|   |   |   |   |   |   \-- scrapegraph-smartscraper-lama-index.py
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- scrapegraph
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_integration.py
|   |   |   |   |   |   \-- test_tools_scrapegraph.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-seltz
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- seltz.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- seltz
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_seltz.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-serpex
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- serpex_example.py
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- serpex
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   \-- test_serpex.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- test_local.py
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-shopify
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- shopify.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- shopify
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_shopify.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-signnow
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- from_env.py
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- signnow
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_delegation.py
|   |   |   |   |   |   |-- test_env_and_bin.py
|   |   |   |   |   |   \-- test_tools_signnow.py
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-slack
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- slack
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_slack.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-tavily-research
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- tavily.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- tavily_research
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_tavily_research.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-text-to-image
|   |   |   |   |   |-- examples
|   |   |   |   |   |   |-- text_to_image-pg.ipynb
|   |   |   |   |   |   \-- text_to_image.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- text_to_image
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_text_to_image.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-typecast
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- typecast_speech.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- typecast
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   \-- test_tools_typecast.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-valyu
|   |   |   |   |   |-- examples
|   |   |   |   |   |   |-- context.py
|   |   |   |   |   |   \-- retriever_example.py
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- valyu
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           \-- retriever.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_valyu.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-vectara-query
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- vectara_query.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- vectara_query
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_vectara_query.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-vector-db
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- vector_db
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_vector_db.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-waii
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- waii.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- waii
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_waii.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-weather
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- weather
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_weather.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-wikipedia
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- wikipedia.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- wikipedia
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_wikipedia.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-wolfram-alpha
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- wolfram_alpha.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- wolfram_alpha
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_wolfram_alpha.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-yahoo-finance
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- yahoo_finance.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- yahoo_finance
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_yahoo_finance.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-tools-yelp
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- yelp.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- tools
|   |   |   |   |   |       \-- yelp
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_tools_yelp.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- requirements.txt
|   |   |   |   |   \-- uv.lock
|   |   |   |   \-- llama-index-tools-zapier
|   |   |   |       |-- examples
|   |   |   |       |   \-- zapier.ipynb
|   |   |   |       |-- llama_index
|   |   |   |       |   \-- tools
|   |   |   |       |       \-- zapier
|   |   |   |       |           |-- __init__.py
|   |   |   |       |           \-- base.py
|   |   |   |       |-- tests
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   \-- test_tools_zapier.py
|   |   |   |       |-- .gitignore
|   |   |   |       |-- CHANGELOG.md
|   |   |   |       |-- LICENSE
|   |   |   |       |-- Makefile
|   |   |   |       |-- pyproject.toml
|   |   |   |       |-- README.md
|   |   |   |       \-- uv.lock
|   |   |   |-- vector_stores
|   |   |   |   |-- llama-index-vector-stores-alibabacloud-mysql
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- vector_stores
|   |   |   |   |   |       \-- alibabacloud_mysql
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_alibabacloud_mysql.py
|   |   |   |   |   |   \-- test_vector_stores_alibabacloud_mysql.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-alibabacloud-opensearch
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- alibabacloud_opensearch
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_alibabacloud_opensearch.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-analyticdb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- analyticdb
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_analyticdb.py
|   |   |   |   |   |   \-- test_vector_stores_analyticdb.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-ApertureDB
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- ApertureDB
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_ApertureDB.py
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-astra-db
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- astra_db
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_astra_db.py
|   |   |   |   |   |   \-- test_vector_stores_astra_db.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-awadb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- awadb
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_awadb.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-awsdocdb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- awsdocdb
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   \-- test_docdb.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-azureaisearch
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- azureaisearch
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       |-- azureaisearch_utils.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_azureaisearch.py
|   |   |   |   |   |   \-- test_vector_stores_cogsearch.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-azurecosmosmongo
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- azurecosmosmongo
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_azurecosmosmongo.py
|   |   |   |   |   |   \-- test_vector_stores_azurecosmosmongo.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-azurecosmosnosql
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- vector_stores
|   |   |   |   |   |       \-- azurecosmosnosql
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_azurecosmosnosql.py
|   |   |   |   |   |   \-- test_vector_stores_azurecosmosnosql.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-azurepostgresql
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- vector_stores
|   |   |   |   |   |       \-- azure_postgres
|   |   |   |   |   |           |-- common
|   |   |   |   |   |           |   |-- aio
|   |   |   |   |   |           |   |   |-- __init__.py
|   |   |   |   |   |           |   |   \-- _connection.py
|   |   |   |   |   |           |   |-- __init__.py
|   |   |   |   |   |           |   |-- _base.py
|   |   |   |   |   |           |   |-- _connection.py
|   |   |   |   |   |           |   \-- _shared.py
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- common
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- test_connection.py
|   |   |   |   |   |   |   \-- test_shared.py
|   |   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |   \-- test_vectorstore.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- conftest.py
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-bagel
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- bagel
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_bagel.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-baiduvectordb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- baiduvectordb
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_baiduvectordb.py
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-bigquery
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- bigquery
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       |-- base.py
|   |   |   |   |   |   |       \-- utils.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- sql_assertions.py
|   |   |   |   |   |   |-- test_add.py
|   |   |   |   |   |   |-- test_delete.py
|   |   |   |   |   |   |-- test_delete_nodes.py
|   |   |   |   |   |   |-- test_get_nodes.py
|   |   |   |   |   |   |-- test_parameterized_queries.py
|   |   |   |   |   |   |-- test_vector_search.py
|   |   |   |   |   |   \-- test_vector_stores_bigquery.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-cassandra
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- cassandra
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_cassandra.py
|   |   |   |   |   |   \-- test_vector_stores_cassandra.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-chroma
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- chroma
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_chromadb.py
|   |   |   |   |   |   |-- test_mmr.py
|   |   |   |   |   |   \-- test_vector_stores_chroma.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-clickhouse
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- clickhouse
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_clickhouse.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- docker-compose.yml
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-couchbase
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- couchbase
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_couchbase_query_vector_store.py
|   |   |   |   |   |   |-- test_couchbase_search_vector_stores.py
|   |   |   |   |   |   \-- vector_index.json
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-dashvector
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- dashvector
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_dashvector.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-databricks
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- databricks
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-db2
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- vector_stores
|   |   |   |   |   |       \-- db2
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_db2.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-deeplake
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- deeplake
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_deeplake.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-docarray
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- docarray
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       |-- base.py
|   |   |   |   |   |   |       |-- hnsw.py
|   |   |   |   |   |   |       \-- in_memory.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_docarray.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-duckdb
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- DuckDBDemo.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- duckdb
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_duckdb.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-dynamodb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- dynamodb
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_dynamodb.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-elasticsearch
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- elasticsearch
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       |-- base.py
|   |   |   |   |   |   |       \-- utils.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- docker-compose.yml
|   |   |   |   |   |   \-- test_vector_stores_elasticsearch.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-epsilla
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- epsilla
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_epsilla.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-faiss
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- faiss
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       |-- base.py
|   |   |   |   |   |   |       \-- map_store.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_faiss.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-firestore
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- firestore
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       |-- base.py
|   |   |   |   |   |   |       \-- utils.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_firestore.py
|   |   |   |   |   |   |-- test_utils.py
|   |   |   |   |   |   \-- test_vector_store_firestore.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-gel
|   |   |   |   |   |-- dbschema
|   |   |   |   |   |   |-- migrations
|   |   |   |   |   |   |   \-- 00001-m1bj5um.edgeql
|   |   |   |   |   |   |-- default.gel
|   |   |   |   |   |   \-- scoping.gel
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- gel
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_gel.py
|   |   |   |   |   |   \-- test_vector_stores_gel.py
|   |   |   |   |   |-- gel.toml
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-google
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- google
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       |-- base.py
|   |   |   |   |   |   |       \-- genai_extension.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_google.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-hnswlib
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- hnswlib
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_hnswlib.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-hologres
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- hologres
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_hologres.py
|   |   |   |   |   |   \-- test_vector_stores_hologres.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-jaguar
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- jaguar
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_jaguar.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-kdbai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- kdbai
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       |-- base.py
|   |   |   |   |   |   |       \-- utils.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-lancedb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- lancedb
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       |-- base.py
|   |   |   |   |   |   |       \-- util.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_lancedb.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-lantern
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- lantern
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_lantern.py
|   |   |   |   |   |   \-- test_vector_stores_lantern.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-lindorm
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- lindorm
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_lindorm_client.py
|   |   |   |   |   |   \-- test_vector_stores_lindorm.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-mariadb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- mariadb
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- docker-compose.yaml
|   |   |   |   |   |   |-- test_mariadb.py
|   |   |   |   |   |   \-- test_vector_stores_mariadb.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-milvus
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- milvus
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       |-- base.py
|   |   |   |   |   |   |       \-- utils.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   \-- test_vector_stores_milvus.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-mongodb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- mongodb
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       |-- base.py
|   |   |   |   |   |   |       |-- index.py
|   |   |   |   |   |   |       \-- pipelines.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_filters.py
|   |   |   |   |   |   |-- test_index_commands.py
|   |   |   |   |   |   |-- test_integration.py
|   |   |   |   |   |   |-- test_vector_stores_mongodb.py
|   |   |   |   |   |   \-- test_vectorstore.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-moorcheh
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- moorcheh
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       |-- base.py
|   |   |   |   |   |   |       \-- utils.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_moorcheh.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-neo4jvector
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- neo4jvector
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_neo4jvector.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-neptune
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- neptune
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_neptune.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-nile
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- multitenant.py
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- nile
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_nile.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-objectbox
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- vector_stores
|   |   |   |   |   |       \-- objectbox
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_objectbox.py
|   |   |   |   |   |   \-- test_vector_stores_objectbox.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-oceanbase
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- oceanbase
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_vector_stores_oceanbase.py
|   |   |   |   |   |   \-- test_vector_stores_oceanbase_unit.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-openGauss
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- openGauss
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       |-- base.py
|   |   |   |   |   |   |       \-- BUILD
|   |   |   |   |   |   |-- BUILD
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- BUILD
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_opengauss.py
|   |   |   |   |   |   \-- test_vector_stores_opengauss.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   \-- README.md
|   |   |   |   |-- llama-index-vector-stores-opensearch
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- opensearch
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- docker-compose.yml
|   |   |   |   |   |   |-- test_opensearch_client.py
|   |   |   |   |   |   \-- test_vector_stores_opensearch.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-oracledb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- vector_stores
|   |   |   |   |   |       \-- oracledb
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_orallamavs.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-pgvecto-rs
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- pgvecto_rs
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_pgvecto_rs.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-pinecone
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- pinecone
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       |-- base.py
|   |   |   |   |   |   |       \-- utils.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_pinecone.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-postgres
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- postgres
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   |-- test_postgres.py
|   |   |   |   |   |   \-- test_vector_stores_postgres.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-qdrant
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- qdrant
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       |-- base.py
|   |   |   |   |   |   |       \-- utils.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   \-- test_vector_stores_qdrant.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-redis
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- redis
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       |-- base.py
|   |   |   |   |   |   |       |-- schema.py
|   |   |   |   |   |   |       \-- utils.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   \-- test_vector_stores_redis.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-relyt
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- relyt
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_relyt.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-rocksetdb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- rocksetdb
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_rocksetdb.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-s3
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- s3
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   \-- test_s3_vector_store.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-singlestoredb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- singlestoredb
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_singlestoredb.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-solr
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- solr
|   |   |   |   |   |   |       |-- client
|   |   |   |   |   |   |       |   |-- __init__.py
|   |   |   |   |   |   |       |   |-- _base.py
|   |   |   |   |   |   |       |   |-- async_.py
|   |   |   |   |   |   |       |   |-- responses.py
|   |   |   |   |   |   |       |   |-- sync.py
|   |   |   |   |   |   |       |   \-- utils.py
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       |-- base.py
|   |   |   |   |   |   |       |-- constants.py
|   |   |   |   |   |   |       |-- query_utils.py
|   |   |   |   |   |   |       \-- types.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- integration
|   |   |   |   |   |   |   \-- test_solr_vector_store.py
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- docker-compose.yml
|   |   |   |   |   |   |-- test_async_client.py
|   |   |   |   |   |   |-- test_client_utils.py
|   |   |   |   |   |   |-- test_solr_vector_store.py
|   |   |   |   |   |   |-- test_solr_vector_store_query_utils.py
|   |   |   |   |   |   |-- test_sync_client.py
|   |   |   |   |   |   \-- test_types.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-supabase
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- supabase
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_supabase.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-tablestore
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- vector_stores
|   |   |   |   |   |       \-- tablestore
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           \-- base.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_tablestore.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-tair
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- tair
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_tair.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-tencentvectordb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- tencentvectordb
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_tencentvectordb.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-tidbvector
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- tidbvector
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_tidbvector.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-timescalevector
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- timescalevector
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-txtai
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- txtai
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_txtai.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-typesense
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- typesense
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_typesense.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-upstash
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- upstash
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_upstash.py
|   |   |   |   |   |   \-- test_vector_stores_upstash.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-vearch
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- VearchDemo.ipynb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- vearch
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_vearch.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-vectorx
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- vectorx
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   \-- test_vector_stores_vectorx.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   \-- README.md
|   |   |   |   |-- llama-index-vector-stores-vertexaivectorsearch
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- vertexaivectorsearch
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       |-- _sdk_manager.py
|   |   |   |   |   |   |       |-- _v2_operations.py
|   |   |   |   |   |   |       |-- base.py
|   |   |   |   |   |   |       \-- utils.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_vertexaivectorsearch.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   |-- uv.lock
|   |   |   |   |   \-- V2_MIGRATION.md
|   |   |   |   |-- llama-index-vector-stores-vespa
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- vespa
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       |-- base.py
|   |   |   |   |   |   |       \-- templates.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   \-- test_vespavectorstore.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- CHANGELOG.md
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-volcenginemysql
|   |   |   |   |   |-- examples
|   |   |   |   |   |   \-- volcengine_mysql_vector_store_demo.py
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- volcengine_mysql
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- test_vector_stores_volcenginemysql.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   \-- README.md
|   |   |   |   |-- llama-index-vector-stores-weaviate
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- weaviate
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       |-- _exceptions.py
|   |   |   |   |   |   |       |-- base.py
|   |   |   |   |   |   |       \-- utils.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- test_to_weaviate_filter.py
|   |   |   |   |   |   \-- test_vector_stores_weaviate.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-wordlift
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- wordlift
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       |-- base.py
|   |   |   |   |   |   |       \-- metadata_filters_to_filters.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- wiremock
|   |   |   |   |   |   |   |-- __files
|   |   |   |   |   |   |   |   |-- account
|   |   |   |   |   |   |   |   |   \-- me
|   |   |   |   |   |   |   |   |       \-- response_1.json
|   |   |   |   |   |   |   |   \-- vector-search
|   |   |   |   |   |   |   |       \-- queries
|   |   |   |   |   |   |   |           \-- response_1.json
|   |   |   |   |   |   |   \-- mappings
|   |   |   |   |   |   |       |-- account
|   |   |   |   |   |   |       |   \-- me
|   |   |   |   |   |   |       |       \-- request_1.json
|   |   |   |   |   |   |       |-- entities
|   |   |   |   |   |   |       |   \-- request_1.json
|   |   |   |   |   |   |       \-- vector-search
|   |   |   |   |   |   |           |-- nodes-collection
|   |   |   |   |   |   |           |   \-- request_1.json
|   |   |   |   |   |   |           \-- queries
|   |   |   |   |   |   |               |-- request_1.json
|   |   |   |   |   |   |               \-- request_2.json
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   \-- test_wordlift.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-vector-stores-yugabytedb
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   |-- vector_stores
|   |   |   |   |   |   |   \-- yugabytedb
|   |   |   |   |   |   |       |-- __init__.py
|   |   |   |   |   |   |       \-- base.py
|   |   |   |   |   |   \-- py.typed
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- conftest.py
|   |   |   |   |   |   |-- README.md
|   |   |   |   |   |   |-- test_vector_stores_yugabytedb.py
|   |   |   |   |   |   \-- test_yugabytedb.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   \-- llama-index-vector-stores-zep
|   |   |   |       |-- llama_index
|   |   |   |       |   |-- vector_stores
|   |   |   |       |   |   \-- zep
|   |   |   |       |   |       |-- __init__.py
|   |   |   |       |   |       \-- base.py
|   |   |   |       |   \-- py.typed
|   |   |   |       |-- tests
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   \-- test_vector_stores_zep.py
|   |   |   |       |-- .gitignore
|   |   |   |       |-- LICENSE
|   |   |   |       |-- Makefile
|   |   |   |       |-- pyproject.toml
|   |   |   |       |-- README.md
|   |   |   |       \-- uv.lock
|   |   |   |-- voice_agents
|   |   |   |   |-- llama-index-voice-agents-elevenlabs
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- voice_agents
|   |   |   |   |   |       \-- elevenlabs
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           |-- events.py
|   |   |   |   |   |           |-- interface.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   |-- test_events.py
|   |   |   |   |   |   \-- test_utils.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   |-- README.md
|   |   |   |   |   \-- uv.lock
|   |   |   |   |-- llama-index-voice-agents-gemini-live
|   |   |   |   |   |-- llama_index
|   |   |   |   |   |   \-- voice_agents
|   |   |   |   |   |       \-- gemini_live
|   |   |   |   |   |           |-- __init__.py
|   |   |   |   |   |           |-- audio_interface.py
|   |   |   |   |   |           |-- base.py
|   |   |   |   |   |           |-- events.py
|   |   |   |   |   |           \-- utils.py
|   |   |   |   |   |-- tests
|   |   |   |   |   |   |-- test_audio_interface.py
|   |   |   |   |   |   |-- test_gemini_live.py
|   |   |   |   |   |   \-- test_utils.py
|   |   |   |   |   |-- .gitignore
|   |   |   |   |   |-- LICENSE
|   |   |   |   |   |-- Makefile
|   |   |   |   |   |-- pyproject.toml
|   |   |   |   |   \-- README.md
|   |   |   |   \-- llama-index-voice-agents-openai
|   |   |   |       |-- llama_index
|   |   |   |       |   \-- voice_agents
|   |   |   |       |       \-- openai
|   |   |   |       |           |-- __init__.py
|   |   |   |       |           |-- audio_interface.py
|   |   |   |       |           |-- base.py
|   |   |   |       |           |-- types.py
|   |   |   |       |           |-- utils.py
|   |   |   |       |           \-- websocket.py
|   |   |   |       |-- tests
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- test_serialization.py
|   |   |   |       |   \-- test_utils.py
|   |   |   |       |-- .gitignore
|   |   |   |       |-- LICENSE
|   |   |   |       |-- Makefile
|   |   |   |       |-- pyproject.toml
|   |   |   |       |-- README.md
|   |   |   |       \-- uv.lock
|   |   |   |-- README.md
|   |   |   \-- test.sh
|   |   |-- llama-index-packs
|   |   |   |-- llama-index-packs-agent-search-retriever
|   |   |   |   |-- examples
|   |   |   |   |   \-- _example.py
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- agent_search_retriever
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-amazon-product-extraction
|   |   |   |   |-- examples
|   |   |   |   |   \-- product_extraction.ipynb
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- amazon_product_extraction
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_amazon_product_extraction.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-arize-phoenix-query-engine
|   |   |   |   |-- examples
|   |   |   |   |   |-- arize_phoenix_llama_pack.ipynb
|   |   |   |   |   \-- example.py
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- arize_phoenix_query_engine
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_arize_phoenix_query_engine.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-auto-merging-retriever
|   |   |   |   |-- examples
|   |   |   |   |   |-- auto_merging_retriever.ipynb
|   |   |   |   |   \-- example.py
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- auto_merging_retriever
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_auto_merging_retriever.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-code-hierarchy
|   |   |   |   |-- examples
|   |   |   |   |   \-- CodeHierarchyNodeParserUsage.ipynb
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- code_hierarchy
|   |   |   |   |           |-- pytree-sitter-queries
|   |   |   |   |           |   |-- tree-sitter-c-tags.scm
|   |   |   |   |           |   |-- tree-sitter-c_sharp-tags.scm
|   |   |   |   |           |   |-- tree-sitter-cpp-tags.scm
|   |   |   |   |           |   |-- tree-sitter-elisp-tags.scm
|   |   |   |   |           |   |-- tree-sitter-elixir-tags.scm
|   |   |   |   |           |   |-- tree-sitter-elm-tags.scm
|   |   |   |   |           |   |-- tree-sitter-go-tags.scm
|   |   |   |   |           |   |-- tree-sitter-java-tags.scm
|   |   |   |   |           |   |-- tree-sitter-javascript-tags.scm
|   |   |   |   |           |   |-- tree-sitter-ocaml-tags.scm
|   |   |   |   |           |   |-- tree-sitter-php-tags.scm
|   |   |   |   |           |   |-- tree-sitter-python-tags.scm
|   |   |   |   |           |   |-- tree-sitter-ql-tags.scm
|   |   |   |   |           |   |-- tree-sitter-ruby-tags.scm
|   |   |   |   |           |   |-- tree-sitter-rust-tags.scm
|   |   |   |   |           |   \-- tree-sitter-typescript-tags.scm
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           |-- base.py
|   |   |   |   |           |-- code_hierarchy.py
|   |   |   |   |           \-- query_engine.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- conftest.py
|   |   |   |   |   |-- test_code_hierarchy_no_skeleton.py
|   |   |   |   |   |-- test_code_hierarchy_with_skeleton.py
|   |   |   |   |   |-- test_code_parse_nodes_special_characters.py
|   |   |   |   |   |-- test_query_engine.py
|   |   |   |   |   \-- test_utility_methods.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- LICENSE
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-cohere-citation-chat
|   |   |   |   |-- examples
|   |   |   |   |   |-- cohere_citation_chat_example.ipynb
|   |   |   |   |   \-- example.py
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- cohere_citation_chat
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           |-- base.py
|   |   |   |   |           |-- citations_context_chat_engine.py
|   |   |   |   |           |-- types.py
|   |   |   |   |           \-- utils.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_cohere_citation_chat.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-deeplake-deepmemory-retriever
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- deeplake_deepmemory_retriever
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_deeplake_deepmemory_retriever.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-deeplake-multimodal-retrieval
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- deeplake_multimodal_retrieval
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_deeplake_multimodal_retrieval.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-dense-x-retrieval
|   |   |   |   |-- examples
|   |   |   |   |   |-- dense_x_retrieval.ipynb
|   |   |   |   |   \-- example.py
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- dense_x_retrieval
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_dense_x_retrieval.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-diff-private-simple-dataset
|   |   |   |   |-- examples
|   |   |   |   |   |-- basic_demo
|   |   |   |   |   |   |-- _create_agnews_simple_dataset.ipynb
|   |   |   |   |   |   |-- demo_usage.ipynb
|   |   |   |   |   |   \-- README.md
|   |   |   |   |   \-- symptom_2_disease
|   |   |   |   |       |-- __init__.py
|   |   |   |   |       |-- _create_symptom_2_disease_simple_dataset.py
|   |   |   |   |       |-- _download_raw_symptom_2_disease_data.py
|   |   |   |   |       |-- error_report.json
|   |   |   |   |       |-- event_handler.py
|   |   |   |   |       |-- main.py
|   |   |   |   |       \-- README.md
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- diff_private_simple_dataset
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           |-- base.py
|   |   |   |   |           |-- events.py
|   |   |   |   |           |-- privacy_mechanism.py
|   |   |   |   |           \-- templates.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- test_packs_diff_private_examples_gen.py
|   |   |   |   |   \-- test_templates.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-evaluator-benchmarker
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- evaluator_benchmarker
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_evaluator_benchmarker.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-fusion-retriever
|   |   |   |   |-- examples
|   |   |   |   |   |-- hybrid_fusion
|   |   |   |   |   |   |-- example.py
|   |   |   |   |   |   \-- hybrid_fusion.ipynb
|   |   |   |   |   \-- query_rewrite
|   |   |   |   |       |-- example.py
|   |   |   |   |       \-- query_rewrite.ipynb
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- fusion_retriever
|   |   |   |   |           |-- hybrid_fusion
|   |   |   |   |           |   |-- __init__.py
|   |   |   |   |           |   \-- base.py
|   |   |   |   |           |-- query_rewrite
|   |   |   |   |           |   |-- __init__.py
|   |   |   |   |           |   \-- base.py
|   |   |   |   |           \-- __init__.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_fusion_retriever.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-fuzzy-citation
|   |   |   |   |-- examples
|   |   |   |   |   \-- fuzzy_citation_example.ipynb
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- fuzzy_citation
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_fuzzy_citation.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-gmail-openai-agent
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- gmail_openai_agent
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_gmail_openai_agent.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-koda-retriever
|   |   |   |   |-- examples
|   |   |   |   |   |-- data
|   |   |   |   |   |   |-- dense_x_retrieval.pdf
|   |   |   |   |   |   |-- llama_beyond_english.pdf
|   |   |   |   |   |   \-- llm_compiler.pdf
|   |   |   |   |   |-- alpha_evaluation.ipynb
|   |   |   |   |   |-- alpha_tuning.ipynb
|   |   |   |   |   |-- quickstart.ipynb
|   |   |   |   |   \-- README.md
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- koda_retriever
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           |-- base.py
|   |   |   |   |           |-- constants.py
|   |   |   |   |           \-- matrix.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- conftest.py
|   |   |   |   |   |-- koda_mocking.py
|   |   |   |   |   |-- monkeypatch.py
|   |   |   |   |   \-- test_koda_retriever.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-llama-dataset-metadata
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- llama_dataset_metadata
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_llama_dataset_metadata.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-llama-guard-moderator
|   |   |   |   |-- examples
|   |   |   |   |   \-- rag_moderator_llama_guard_pack.ipynb
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- llama_guard_moderator
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_llama_guard_moderator.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-llava-completion
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- llava_completion
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_llava_completion.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-longrag
|   |   |   |   |-- examples
|   |   |   |   |   |-- data
|   |   |   |   |   |   |-- being_a_noob.txt
|   |   |   |   |   |   |-- four_quadrants_of_conformism.txt
|   |   |   |   |   |   |-- haters.txt
|   |   |   |   |   |   |-- how_to_make_pgh_a_startup_hub.txt
|   |   |   |   |   |   |-- how_to_raise_money.txt
|   |   |   |   |   |   |-- investor_herd_dynamics.txt
|   |   |   |   |   |   |-- lies_we_tell_kids.txt
|   |   |   |   |   |   |-- mean_people_fail.txt
|   |   |   |   |   |   |-- the_best_essay.txt
|   |   |   |   |   |   |-- two_kinds_of_moderate.txt
|   |   |   |   |   |   \-- what_i_worked_on.txt
|   |   |   |   |   \-- longrag.ipynb
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- longrag
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_longrag.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-mixture-of-agents
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- mixture_of_agents
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_mixture_of_agents.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-multi-tenancy-rag
|   |   |   |   |-- examples
|   |   |   |   |   \-- multi_tenancy_rag.ipynb
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- multi_tenancy_rag
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_multi_tenancy_rag.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-multidoc-autoretrieval
|   |   |   |   |-- examples
|   |   |   |   |   \-- multidoc_autoretrieval.ipynb
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- multidoc_autoretrieval
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_multidoc_autoretrieval.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-nebulagraph-query-engine
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- nebulagraph_query_engine
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_nebulagraph_query_engine.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-neo4j-query-engine
|   |   |   |   |-- examples
|   |   |   |   |   \-- llama_packs_neo4j.ipynb
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- neo4j_query_engine
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_neo4j_query_engine.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-node-parser-semantic-chunking
|   |   |   |   |-- examples
|   |   |   |   |   \-- semantic_chunking.ipynb
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- node_parser_semantic_chunking
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_node_parser.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-ollama-query-engine
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- ollama_query_engine
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_ollama_query_engine.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-panel-chatbot
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- panel_chatbot
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           |-- app.py
|   |   |   |   |           |-- base.py
|   |   |   |   |           |-- llama_by_sophia_yang.png
|   |   |   |   |           \-- panel_chatbot.png
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_panel_chatbot.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-raft-dataset
|   |   |   |   |-- examples
|   |   |   |   |   \-- raft_dataset.ipynb
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- raft_dataset
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_raft_dataset.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-rag-evaluator
|   |   |   |   |-- examples
|   |   |   |   |   \-- example.py
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- rag_evaluator
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_rag_evaluator.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-ragatouille-retriever
|   |   |   |   |-- examples
|   |   |   |   |   |-- colbertv2.pdf
|   |   |   |   |   \-- ragatouille_retriever.ipynb
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- ragatouille_retriever
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_ragatouille_retriever.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-raptor
|   |   |   |   |-- examples
|   |   |   |   |   |-- raptor
|   |   |   |   |   |   |-- 81db1dbe-a06d-43a6-ba07-875398bc33a7
|   |   |   |   |   |   |   |-- data_level0.bin
|   |   |   |   |   |   |   |-- header.bin
|   |   |   |   |   |   |   |-- length.bin
|   |   |   |   |   |   |   \-- link_lists.bin
|   |   |   |   |   |   \-- chroma.sqlite3
|   |   |   |   |   \-- raptor.ipynb
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- raptor
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           |-- base.py
|   |   |   |   |           \-- clustering.py
|   |   |   |   |-- tests_llamadev_ignore
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_raptor.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-recursive-retriever
|   |   |   |   |-- examples
|   |   |   |   |   |-- embedded_tables.ipynb
|   |   |   |   |   \-- small_to_big.ipynb
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- recursive_retriever
|   |   |   |   |           |-- embedded_tables_unstructured
|   |   |   |   |           |   |-- __init__.py
|   |   |   |   |           |   \-- base.py
|   |   |   |   |           |-- small_to_big
|   |   |   |   |           |   |-- __init__.py
|   |   |   |   |           |   \-- base.py
|   |   |   |   |           \-- __init__.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_recursive_retriever.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-resume-screener
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- resume_screener
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-retry-engine-weaviate
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- retry_engine_weaviate
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_retry_engine_weaviate.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-searchain
|   |   |   |   |-- examples
|   |   |   |   |   \-- searchain.ipynb
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- searchain
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           |-- base.py
|   |   |   |   |           \-- BUILD
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- BUILD
|   |   |   |   |   \-- test_packs_searchain.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-self-discover
|   |   |   |   |-- examples
|   |   |   |   |   \-- self_discover.ipynb
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- self_discover
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_self_discover.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-self-rag
|   |   |   |   |-- examples
|   |   |   |   |   \-- self_rag.ipynb
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- self_rag
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_self_rag.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-sentence-window-retriever
|   |   |   |   |-- examples
|   |   |   |   |   \-- sentence_window.ipynb
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- sentence_window_retriever
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_sentence_window_retriever.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-snowflake-query-engine
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- snowflake_query_engine
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_snowflake_query_engine.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-stock-market-data-query-engine
|   |   |   |   |-- examples
|   |   |   |   |   \-- stock_market_data_query_engine.ipynb
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- stock_market_data_query_engine
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_stock_market_data_query_engine.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-streamlit-chatbot
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- streamlit_chatbot
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_streamlit_chatbot.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-sub-question-weaviate
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- sub_question_weaviate
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_sub_question_weaviate.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-timescale-vector-autoretrieval
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- timescale_vector_autoretrieval
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-trulens-eval-packs
|   |   |   |   |-- examples
|   |   |   |   |   \-- trulens_eval_llama_packs.ipynb
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- trulens_eval_packs
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_trulens_eval_packs.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-vectara-rag
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- vectara_rag
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_vectara_rag.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-voyage-query-engine
|   |   |   |   |-- examples
|   |   |   |   |   \-- example.py
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- voyage_query_engine
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_voyage_query_engine.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- CHANGELOG.md
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-zenguard
|   |   |   |   |-- examples
|   |   |   |   |   \-- zenguard.ipynb
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- zenguard
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_zenguard.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-packs-zephyr-query-engine
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- packs
|   |   |   |   |       \-- zephyr_query_engine
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_packs_zephyr_query_engine.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   \-- README.md
|   |   |-- llama-index-utils
|   |   |   |-- llama-index-utils-azure
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- utils
|   |   |   |   |       \-- azure
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- table.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   |-- requirements.txt
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-utils-huggingface
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- utils
|   |   |   |   |       \-- huggingface
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-utils-oracleai
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- utils
|   |   |   |   |       \-- oracleai
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           \-- base.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- test_utils_oracleai.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   \-- uv.lock
|   |   |   |-- llama-index-utils-qianfan
|   |   |   |   |-- llama_index
|   |   |   |   |   \-- utils
|   |   |   |   |       \-- qianfan
|   |   |   |   |           |-- __init__.py
|   |   |   |   |           |-- apis.py
|   |   |   |   |           |-- authorization.py
|   |   |   |   |           \-- client.py
|   |   |   |   |-- tests
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- test_apis.py
|   |   |   |   |   |-- test_authorization.py
|   |   |   |   |   \-- test_client.py
|   |   |   |   |-- .gitignore
|   |   |   |   |-- LICENSE
|   |   |   |   |-- Makefile
|   |   |   |   |-- pyproject.toml
|   |   |   |   |-- README.md
|   |   |   |   \-- uv.lock
|   |   |   \-- README.md
|   |   |-- scripts
|   |   |   |-- integration_health_check.py
|   |   |   \-- publish_packages.sh
|   |   |-- .gitignore
|   |   |-- .pre-commit-config.yaml
|   |   |-- .readthedocs.yaml
|   |   |-- CHANGELOG.md
|   |   |-- CITATION.cff
|   |   |-- CODE_OF_CONDUCT.md
|   |   |-- CONTRIBUTING.md
|   |   |-- LICENSE
|   |   |-- Makefile
|   |   |-- pyproject.toml
|   |   |-- README.md
|   |   |-- RELEASE_HEAD.md
|   |   |-- SECURITY.md
|   |   |-- STALE.md
|   |   \-- uv.lock
|   |-- openeducat_erp
|   |   |-- .github
|   |   |   \-- ISSUE_TEMPLATE
|   |   |       \-- bug_report.md
|   |   |-- openeducat_activity
|   |   |   |-- data
|   |   |   |   \-- activity_type_data.xml
|   |   |   |-- demo
|   |   |   |   \-- activity_demo.xml
|   |   |   |-- i18n
|   |   |   |   |-- ar_001.po
|   |   |   |   |-- da_DK.po
|   |   |   |   |-- de.po
|   |   |   |   |-- es.po
|   |   |   |   |-- fa.po
|   |   |   |   |-- fr.po
|   |   |   |   |-- id.po
|   |   |   |   |-- it.po
|   |   |   |   |-- lt.po
|   |   |   |   |-- nl.po
|   |   |   |   |-- openeducat_activity.pot
|   |   |   |   |-- pt.po
|   |   |   |   |-- ru.po
|   |   |   |   |-- th.po
|   |   |   |   |-- vi.po
|   |   |   |   |-- vi_VN.po
|   |   |   |   |-- zh_CN.po
|   |   |   |   \-- zh_HK.po
|   |   |   |-- menus
|   |   |   |   \-- op_menu.xml
|   |   |   |-- models
|   |   |   |   |-- __init__.py
|   |   |   |   |-- activity.py
|   |   |   |   |-- activity_type.py
|   |   |   |   \-- student.py
|   |   |   |-- security
|   |   |   |   |-- ir.model.access.csv
|   |   |   |   \-- op_security.xml
|   |   |   |-- static
|   |   |   |   \-- description
|   |   |   |       |-- activity.png
|   |   |   |       |-- assignment-annotation-icon.png
|   |   |   |       |-- campus-icon.svg
|   |   |   |       |-- courses-icon 1.svg
|   |   |   |       |-- faculties-icon.svg
|   |   |   |       |-- fees.svg
|   |   |   |       |-- g-2-img.png
|   |   |   |       |-- g2-img.svg
|   |   |   |       |-- grade-book-icon.svg
|   |   |   |       |-- help.jpg
|   |   |   |       |-- hr.png
|   |   |   |       |-- icon.png
|   |   |   |       |-- index.html
|   |   |   |       |-- inventory.svg
|   |   |   |       |-- kpi-dashboard-icon.svg
|   |   |   |       |-- lms-icon.svg
|   |   |   |       |-- news.svg
|   |   |   |       |-- notice-board-icon.svg
|   |   |   |       |-- openeducat-activity_banner.jpg
|   |   |   |       |-- openeducat_account_financial_reports.svg
|   |   |   |       |-- openeducat_activity_banner.jpg
|   |   |   |       |-- openeducat_admission.svg
|   |   |   |       |-- openeducat_alumni_enterprise.svg
|   |   |   |       |-- openeducat_assignment.svg
|   |   |   |       |-- openeducat_attendance.svg
|   |   |   |       |-- openeducat_classroom.svg
|   |   |   |       |-- openeducat_exam.svg
|   |   |   |       |-- openeducat_library.svg
|   |   |   |       |-- openeducat_logo.png
|   |   |   |       |-- openeducat_timetable.svg
|   |   |   |       |-- sis-icon.svg
|   |   |   |       |-- sourceforge-img.svg
|   |   |   |       |-- students-icon.svg
|   |   |   |       \-- transportation-icon.svg
|   |   |   |-- tests
|   |   |   |   |-- __init__.py
|   |   |   |   |-- test_activity.py
|   |   |   |   \-- test_activity_common.py
|   |   |   |-- views
|   |   |   |   |-- activity_type_view.xml
|   |   |   |   |-- activity_view.xml
|   |   |   |   \-- student_view.xml
|   |   |   |-- wizard
|   |   |   |   |-- __init__.py
|   |   |   |   |-- student_migrate_wizard.py
|   |   |   |   \-- student_migrate_wizard_view.xml
|   |   |   |-- __init__.py
|   |   |   |-- __manifest__.py
|   |   |   \-- README.rst
|   |   |-- openeducat_admission
|   |   |   |-- data
|   |   |   |   |-- admission_sequence.xml
|   |   |   |   \-- parameter_data.xml
|   |   |   |-- demo
|   |   |   |   |-- admission_demo.xml
|   |   |   |   \-- admission_register_demo.xml
|   |   |   |-- i18n
|   |   |   |   |-- ar_001.po
|   |   |   |   |-- da_DK.po
|   |   |   |   |-- de.po
|   |   |   |   |-- es.po
|   |   |   |   |-- fa.po
|   |   |   |   |-- fr.po
|   |   |   |   |-- id.po
|   |   |   |   |-- it.po
|   |   |   |   |-- lt.po
|   |   |   |   |-- nl.po
|   |   |   |   |-- openeducat_admission.pot
|   |   |   |   |-- pt.po
|   |   |   |   |-- ru.po
|   |   |   |   |-- th.po
|   |   |   |   |-- vi.po
|   |   |   |   |-- vi_VN.po
|   |   |   |   |-- zh_CN.po
|   |   |   |   \-- zh_HK.po
|   |   |   |-- menus
|   |   |   |   \-- op_menu.xml
|   |   |   |-- models
|   |   |   |   |-- __init__.py
|   |   |   |   |-- admission.py
|   |   |   |   \-- admission_register.py
|   |   |   |-- report
|   |   |   |   |-- __init__.py
|   |   |   |   |-- admission_analysis_report.py
|   |   |   |   |-- report_admission_analysis.xml
|   |   |   |   \-- report_menu.xml
|   |   |   |-- security
|   |   |   |   |-- ir.model.access.csv
|   |   |   |   \-- op_admission_security.xml
|   |   |   |-- static
|   |   |   |   |-- description
|   |   |   |   |   |-- admission.png
|   |   |   |   |   |-- admission_analysis.png
|   |   |   |   |   |-- admission_register.png
|   |   |   |   |   |-- admission_register2.png
|   |   |   |   |   |-- assignment-annotation-icon.png
|   |   |   |   |   |-- campus-icon.svg
|   |   |   |   |   |-- courses-icon 1.svg
|   |   |   |   |   |-- faculties-icon.svg
|   |   |   |   |   |-- fees.svg
|   |   |   |   |   |-- fees_payment.png
|   |   |   |   |   |-- g-2-img.png
|   |   |   |   |   |-- g2-img.svg
|   |   |   |   |   |-- grade-book-icon.svg
|   |   |   |   |   |-- help.jpg
|   |   |   |   |   |-- hr.png
|   |   |   |   |   |-- icon.png
|   |   |   |   |   |-- index.html
|   |   |   |   |   |-- inventory.svg
|   |   |   |   |   |-- kpi-dashboard-icon.svg
|   |   |   |   |   |-- lms-icon.svg
|   |   |   |   |   |-- news.svg
|   |   |   |   |   |-- notice-board-icon.svg
|   |   |   |   |   |-- openeducat-admission_banner.jpg
|   |   |   |   |   |-- openeducat_account_financial_reports.svg
|   |   |   |   |   |-- openeducat_admission.svg
|   |   |   |   |   |-- openeducat_admission_banner.jpg
|   |   |   |   |   |-- openeducat_alumni_enterprise.svg
|   |   |   |   |   |-- openeducat_assignment.svg
|   |   |   |   |   |-- openeducat_attendance.svg
|   |   |   |   |   |-- openeducat_classroom.svg
|   |   |   |   |   |-- openeducat_exam.svg
|   |   |   |   |   |-- openeducat_library.svg
|   |   |   |   |   |-- openeducat_logo.png
|   |   |   |   |   |-- openeducat_timetable.svg
|   |   |   |   |   |-- sis-icon.svg
|   |   |   |   |   |-- sourceforge-img.svg
|   |   |   |   |   |-- students-icon.svg
|   |   |   |   |   \-- transportation-icon.svg
|   |   |   |   |-- img
|   |   |   |   |   |-- Invoice_btn.png
|   |   |   |   |   |-- student_1.jpg
|   |   |   |   |   |-- student_10.jpg
|   |   |   |   |   |-- student_11.jpg
|   |   |   |   |   |-- student_12.jpg
|   |   |   |   |   |-- student_13.jpg
|   |   |   |   |   |-- student_14.jpg
|   |   |   |   |   |-- student_15.jpg
|   |   |   |   |   |-- student_16.jpg
|   |   |   |   |   |-- student_17.jpg
|   |   |   |   |   |-- student_18.jpg
|   |   |   |   |   |-- student_19.jpg
|   |   |   |   |   |-- student_2.jpg
|   |   |   |   |   |-- student_20.jpg
|   |   |   |   |   |-- student_21.jpg
|   |   |   |   |   |-- student_22.jpg
|   |   |   |   |   |-- student_23.jpg
|   |   |   |   |   |-- student_24.jpg
|   |   |   |   |   |-- student_25.jpg
|   |   |   |   |   |-- student_3.jpg
|   |   |   |   |   |-- student_4.jpg
|   |   |   |   |   |-- student_5.jpg
|   |   |   |   |   |-- student_6.jpg
|   |   |   |   |   |-- student_7.jpg
|   |   |   |   |   |-- student_8.jpg
|   |   |   |   |   \-- student_9.jpg
|   |   |   |   \-- xls
|   |   |   |       \-- op_admission.xls
|   |   |   |-- tests
|   |   |   |   |-- __init__.py
|   |   |   |   |-- test_admission.py
|   |   |   |   \-- test_admission_common.py
|   |   |   |-- views
|   |   |   |   |-- admission_register_view.xml
|   |   |   |   \-- admission_view.xml
|   |   |   |-- wizard
|   |   |   |   |-- __init__.py
|   |   |   |   |-- admission_analysis_wizard.py
|   |   |   |   \-- admission_analysis_wizard_view.xml
|   |   |   |-- __init__.py
|   |   |   |-- __manifest__.py
|   |   |   \-- README.rst
|   |   |-- openeducat_assignment
|   |   |   |-- data
|   |   |   |   \-- action_rule_data.xml
|   |   |   |-- demo
|   |   |   |   |-- assignment_demo.xml
|   |   |   |   |-- assignment_sub_line_demo.xml
|   |   |   |   \-- assignment_type_demo.xml
|   |   |   |-- i18n
|   |   |   |   |-- ar_001.po
|   |   |   |   |-- da_DK.po
|   |   |   |   |-- de.po
|   |   |   |   |-- es.po
|   |   |   |   |-- fa.po
|   |   |   |   |-- fr.po
|   |   |   |   |-- id.po
|   |   |   |   |-- it.po
|   |   |   |   |-- lt.po
|   |   |   |   |-- nl.po
|   |   |   |   |-- openeducat_assignment.pot
|   |   |   |   |-- pt.po
|   |   |   |   |-- ru.po
|   |   |   |   |-- th.po
|   |   |   |   |-- vi.po
|   |   |   |   |-- vi_VN.po
|   |   |   |   |-- zh.po
|   |   |   |   |-- zh_CN.po
|   |   |   |   \-- zh_HK.po
|   |   |   |-- menus
|   |   |   |   \-- op_menu.xml
|   |   |   |-- models
|   |   |   |   |-- __init__.py
|   |   |   |   |-- assignment.py
|   |   |   |   |-- assignment_sub_line.py
|   |   |   |   |-- assignment_type.py
|   |   |   |   \-- student.py
|   |   |   |-- security
|   |   |   |   |-- ir.model.access.csv
|   |   |   |   \-- op_security.xml
|   |   |   |-- static
|   |   |   |   \-- description
|   |   |   |       |-- assignment-annotation-icon.png
|   |   |   |       |-- assignment.png
|   |   |   |       |-- assignment_submission.png
|   |   |   |       |-- campus-icon.svg
|   |   |   |       |-- courses-icon 1.svg
|   |   |   |       |-- faculties-icon.svg
|   |   |   |       |-- fees.svg
|   |   |   |       |-- g-2-img.png
|   |   |   |       |-- g2-img.svg
|   |   |   |       |-- grade-book-icon.svg
|   |   |   |       |-- help.jpg
|   |   |   |       |-- hr.png
|   |   |   |       |-- icon.png
|   |   |   |       |-- index.html
|   |   |   |       |-- inventory.svg
|   |   |   |       |-- kpi-dashboard-icon.svg
|   |   |   |       |-- lms-icon.svg
|   |   |   |       |-- news.svg
|   |   |   |       |-- notice-board-icon.svg
|   |   |   |       |-- openeducat-assignment_banner.jpg
|   |   |   |       |-- openeducat_account_financial_reports.svg
|   |   |   |       |-- openeducat_admission.svg
|   |   |   |       |-- openeducat_alumni_enterprise.svg
|   |   |   |       |-- openeducat_assignment.svg
|   |   |   |       |-- openeducat_assignment_banner.jpg
|   |   |   |       |-- openeducat_attendance.svg
|   |   |   |       |-- openeducat_classroom.svg
|   |   |   |       |-- openeducat_exam.svg
|   |   |   |       |-- openeducat_library.svg
|   |   |   |       |-- openeducat_logo.png
|   |   |   |       |-- openeducat_timetable.svg
|   |   |   |       |-- sis-icon.svg
|   |   |   |       |-- sourceforge-img.svg
|   |   |   |       |-- students-icon.svg
|   |   |   |       \-- transportation-icon.svg
|   |   |   |-- tests
|   |   |   |   |-- __init__.py
|   |   |   |   |-- test_assignment.py
|   |   |   |   \-- test_assignment_common.py
|   |   |   |-- views
|   |   |   |   |-- assignment_sub_line_view.xml
|   |   |   |   |-- assignment_type_view.xml
|   |   |   |   |-- assignment_view.xml
|   |   |   |   \-- student_view.xml
|   |   |   |-- __init__.py
|   |   |   |-- __manifest__.py
|   |   |   \-- README.rst
|   |   |-- openeducat_attendance
|   |   |   |-- controllers
|   |   |   |   |-- __init__.py
|   |   |   |   \-- app_main.py
|   |   |   |-- data
|   |   |   |   \-- attendance_sheet_sequence.xml
|   |   |   |-- demo
|   |   |   |   |-- attendance_line_demo.xml
|   |   |   |   |-- attendance_register_demo.xml
|   |   |   |   |-- attendance_sheet_demo.xml
|   |   |   |   \-- attendance_type_demo.xml
|   |   |   |-- i18n
|   |   |   |   |-- ar_001.po
|   |   |   |   |-- ar_AA.po
|   |   |   |   |-- da_DK.po
|   |   |   |   |-- de.po
|   |   |   |   |-- es.po
|   |   |   |   |-- fa.po
|   |   |   |   |-- fr.po
|   |   |   |   |-- id.po
|   |   |   |   |-- it.po
|   |   |   |   |-- lt.po
|   |   |   |   |-- nl.po
|   |   |   |   |-- openeducat_attendance.pot
|   |   |   |   |-- pt.po
|   |   |   |   |-- ru.po
|   |   |   |   |-- th.po
|   |   |   |   |-- vi.po
|   |   |   |   |-- vi_VN.po
|   |   |   |   |-- zh.po
|   |   |   |   |-- zh_CN.po
|   |   |   |   \-- zh_HK.po
|   |   |   |-- menus
|   |   |   |   \-- op_menu.xml
|   |   |   |-- models
|   |   |   |   |-- __init__.py
|   |   |   |   |-- attendance_line.py
|   |   |   |   |-- attendance_register.py
|   |   |   |   |-- attendance_session.py
|   |   |   |   |-- attendance_sheet.py
|   |   |   |   |-- attendance_type.py
|   |   |   |   \-- student.py
|   |   |   |-- report
|   |   |   |   |-- __init__.py
|   |   |   |   |-- report_menu.xml
|   |   |   |   |-- student_attendance_report.py
|   |   |   |   \-- student_attendance_report.xml
|   |   |   |-- security
|   |   |   |   |-- ir.model.access.csv
|   |   |   |   \-- op_security.xml
|   |   |   |-- static
|   |   |   |   \-- description
|   |   |   |       |-- assignment-annotation-icon.png
|   |   |   |       |-- attendance_register.png
|   |   |   |       |-- attendance_report.png
|   |   |   |       |-- attendance_sheet.png
|   |   |   |       |-- campus-icon.svg
|   |   |   |       |-- courses-icon 1.svg
|   |   |   |       |-- faculties-icon.svg
|   |   |   |       |-- fees.svg
|   |   |   |       |-- g-2-img.png
|   |   |   |       |-- g2-img.svg
|   |   |   |       |-- grade-book-icon.svg
|   |   |   |       |-- help.jpg
|   |   |   |       |-- hr.png
|   |   |   |       |-- icon.png
|   |   |   |       |-- index.html
|   |   |   |       |-- inventory.svg
|   |   |   |       |-- kpi-dashboard-icon.svg
|   |   |   |       |-- lms-icon.svg
|   |   |   |       |-- news.svg
|   |   |   |       |-- notice-board-icon.svg
|   |   |   |       |-- openeducat-attendance_banner.jpg
|   |   |   |       |-- openeducat_account_financial_reports.svg
|   |   |   |       |-- openeducat_admission.svg
|   |   |   |       |-- openeducat_alumni_enterprise.svg
|   |   |   |       |-- openeducat_assignment.svg
|   |   |   |       |-- openeducat_attendance.svg
|   |   |   |       |-- openeducat_attendance_banner.jpg
|   |   |   |       |-- openeducat_classroom.svg
|   |   |   |       |-- openeducat_exam.svg
|   |   |   |       |-- openeducat_library.svg
|   |   |   |       |-- openeducat_logo.png
|   |   |   |       |-- openeducat_timetable.svg
|   |   |   |       |-- sis-icon.svg
|   |   |   |       |-- sourceforge-img.svg
|   |   |   |       |-- students-icon.svg
|   |   |   |       |-- take_attendance.png
|   |   |   |       \-- transportation-icon.svg
|   |   |   |-- tests
|   |   |   |   |-- __init__.py
|   |   |   |   |-- test_attendance.py
|   |   |   |   \-- test_attendance_common.py
|   |   |   |-- views
|   |   |   |   |-- attendance_line_view.xml
|   |   |   |   |-- attendance_register_view.xml
|   |   |   |   |-- attendance_session_view.xml
|   |   |   |   |-- attendance_sheet_view.xml
|   |   |   |   |-- attendance_type_view.xml
|   |   |   |   \-- student_view.xml
|   |   |   |-- wizards
|   |   |   |   |-- __init__.py
|   |   |   |   |-- student_attendance_wizard.py
|   |   |   |   \-- student_attendance_wizard_view.xml
|   |   |   |-- __init__.py
|   |   |   |-- __manifest__.py
|   |   |   \-- README.rst
|   |   |-- openeducat_classroom
|   |   |   |-- demo
|   |   |   |   |-- classroom_demo.xml
|   |   |   |   \-- facility_line_demo.xml
|   |   |   |-- i18n
|   |   |   |   |-- ar_001.po
|   |   |   |   |-- da_DK.po
|   |   |   |   |-- de.po
|   |   |   |   |-- es.po
|   |   |   |   |-- fa.po
|   |   |   |   |-- fr.po
|   |   |   |   |-- id.po
|   |   |   |   |-- it.po
|   |   |   |   |-- lt.po
|   |   |   |   |-- nl.po
|   |   |   |   |-- openeducat_classroom.pot
|   |   |   |   |-- pt.po
|   |   |   |   |-- ru.po
|   |   |   |   |-- th.po
|   |   |   |   |-- vi.po
|   |   |   |   |-- vi_VN.po
|   |   |   |   |-- zh.po
|   |   |   |   |-- zh_CN.po
|   |   |   |   \-- zh_HK.po
|   |   |   |-- menus
|   |   |   |   \-- op_menu.xml
|   |   |   |-- models
|   |   |   |   |-- __init__.py
|   |   |   |   |-- asset.py
|   |   |   |   |-- classroom.py
|   |   |   |   \-- facility_line.py
|   |   |   |-- security
|   |   |   |   |-- ir.model.access.csv
|   |   |   |   \-- op_classroom_security.xml
|   |   |   |-- static
|   |   |   |   \-- description
|   |   |   |       |-- assignment-annotation-icon.png
|   |   |   |       |-- campus-icon.svg
|   |   |   |       |-- classroom.png
|   |   |   |       |-- courses-icon 1.svg
|   |   |   |       |-- faculties-icon.svg
|   |   |   |       |-- fees.svg
|   |   |   |       |-- g-2-img.png
|   |   |   |       |-- g2-img.svg
|   |   |   |       |-- grade-book-icon.svg
|   |   |   |       |-- help.jpg
|   |   |   |       |-- hr.png
|   |   |   |       |-- icon.png
|   |   |   |       |-- index.html
|   |   |   |       |-- inventory.svg
|   |   |   |       |-- kpi-dashboard-icon.svg
|   |   |   |       |-- lms-icon.svg
|   |   |   |       |-- news.svg
|   |   |   |       |-- notice-board-icon.svg
|   |   |   |       |-- openeducat-classroom_banner.jpg
|   |   |   |       |-- openeducat_account_financial_reports.svg
|   |   |   |       |-- openeducat_admission.svg
|   |   |   |       |-- openeducat_alumni_enterprise.svg
|   |   |   |       |-- openeducat_assignment.svg
|   |   |   |       |-- openeducat_attendance.svg
|   |   |   |       |-- openeducat_classroom.svg
|   |   |   |       |-- openeducat_classroom_banner.jpg
|   |   |   |       |-- openeducat_exam.svg
|   |   |   |       |-- openeducat_library.svg
|   |   |   |       |-- openeducat_logo.png
|   |   |   |       |-- openeducat_timetable.svg
|   |   |   |       |-- sis-icon.svg
|   |   |   |       |-- sourceforge-img.svg
|   |   |   |       |-- students-icon.svg
|   |   |   |       \-- transportation-icon.svg
|   |   |   |-- tests
|   |   |   |   |-- __init__.py
|   |   |   |   |-- test_classroom.py
|   |   |   |   \-- test_classroom_common.py
|   |   |   |-- views
|   |   |   |   \-- classroom_view.xml
|   |   |   |-- __init__.py
|   |   |   |-- __manifest__.py
|   |   |   \-- README.rst
|   |   |-- openeducat_core
|   |   |   |-- controllers
|   |   |   |   |-- __init__.py
|   |   |   |   \-- app_main.py
|   |   |   |-- data
|   |   |   |   |-- ir_cron_data.xml
|   |   |   |   |-- res_partner_data.xml
|   |   |   |   \-- sequence_student_bonafide.xml
|   |   |   |-- demo
|   |   |   |   |-- base_demo.xml
|   |   |   |   |-- category_demo.xml
|   |   |   |   |-- department_demo.xml
|   |   |   |   |-- faculty_demo.xml
|   |   |   |   |-- op.batch.csv
|   |   |   |   |-- op.course.csv
|   |   |   |   |-- op.program.csv
|   |   |   |   |-- op.program.level.csv
|   |   |   |   |-- op.subject.csv
|   |   |   |   |-- op_academic_term_demo.xml
|   |   |   |   |-- op_academic_year_demo.xml
|   |   |   |   |-- res_condig_fav_icon.xml
|   |   |   |   |-- res_partner_demo.xml
|   |   |   |   |-- res_users_demo.xml
|   |   |   |   |-- student_course_demo.xml
|   |   |   |   \-- student_demo.xml
|   |   |   |-- i18n
|   |   |   |   |-- ar_001.po
|   |   |   |   |-- da_DK.po
|   |   |   |   |-- de.po
|   |   |   |   |-- es.po
|   |   |   |   |-- fa.po
|   |   |   |   |-- fr.po
|   |   |   |   |-- id.po
|   |   |   |   |-- it.po
|   |   |   |   |-- lt.po
|   |   |   |   |-- nl.po
|   |   |   |   |-- openeducat_core.pot
|   |   |   |   |-- pt.po
|   |   |   |   |-- ru.po
|   |   |   |   |-- th.po
|   |   |   |   |-- vi.po
|   |   |   |   |-- vi_VN.po
|   |   |   |   |-- zh.po
|   |   |   |   |-- zh_CN.po
|   |   |   |   |-- zh_HK.po
|   |   |   |   \-- zh_TW.po
|   |   |   |-- menu
|   |   |   |   |-- openeducat_core_menu.xml
|   |   |   |   \-- student_menu.xml
|   |   |   |-- models
|   |   |   |   |-- __init__.py
|   |   |   |   |-- batch.py
|   |   |   |   |-- category.py
|   |   |   |   |-- course.py
|   |   |   |   |-- department.py
|   |   |   |   |-- faculty.py
|   |   |   |   |-- hr.py
|   |   |   |   |-- op_academic_term.py
|   |   |   |   |-- op_academic_year.py
|   |   |   |   |-- program.py
|   |   |   |   |-- res_company.py
|   |   |   |   |-- res_config_setting.py
|   |   |   |   |-- student.py
|   |   |   |   |-- student_portal.py
|   |   |   |   |-- subject.py
|   |   |   |   |-- subject_registration.py
|   |   |   |   \-- update.py
|   |   |   |-- report
|   |   |   |   |-- __init__.py
|   |   |   |   |-- bonafide_report.py
|   |   |   |   |-- report_menu.xml
|   |   |   |   |-- report_student_bonafide.xml
|   |   |   |   \-- report_student_idcard.xml
|   |   |   |-- security
|   |   |   |   |-- ir.model.access.csv
|   |   |   |   \-- op_security.xml
|   |   |   |-- static
|   |   |   |   |-- description
|   |   |   |   |   |-- assignment-annotation-icon.png
|   |   |   |   |   |-- batch.png
|   |   |   |   |   |-- campus-icon.svg
|   |   |   |   |   |-- courses-icon 1.svg
|   |   |   |   |   |-- courses.png
|   |   |   |   |   |-- faculties-icon.svg
|   |   |   |   |   |-- faculty.png
|   |   |   |   |   |-- fees.svg
|   |   |   |   |   |-- g-2-img.png
|   |   |   |   |   |-- g2-img.svg
|   |   |   |   |   |-- grade-book-icon.svg
|   |   |   |   |   |-- help.jpg
|   |   |   |   |   |-- hr.png
|   |   |   |   |   |-- icon.png
|   |   |   |   |   |-- icon_faculty.png
|   |   |   |   |   |-- icon_student.png
|   |   |   |   |   |-- index.html
|   |   |   |   |   |-- inventory.svg
|   |   |   |   |   |-- kpi-dashboard-icon.svg
|   |   |   |   |   |-- lms-icon.svg
|   |   |   |   |   |-- news.svg
|   |   |   |   |   |-- notice-board-icon.svg
|   |   |   |   |   |-- openeducat_account_financial_reports.svg
|   |   |   |   |   |-- openeducat_admission.svg
|   |   |   |   |   |-- openeducat_alumni_enterprise.svg
|   |   |   |   |   |-- openeducat_assignment.svg
|   |   |   |   |   |-- openeducat_attendance.svg
|   |   |   |   |   |-- openeducat_classroom.svg
|   |   |   |   |   |-- openeducat_core_banner.jpg
|   |   |   |   |   |-- openeducat_exam.svg
|   |   |   |   |   |-- openeducat_library.svg
|   |   |   |   |   |-- openeducat_logo.png
|   |   |   |   |   |-- openeducat_timetable.svg
|   |   |   |   |   |-- sis-icon.svg
|   |   |   |   |   |-- sis.png
|   |   |   |   |   |-- sourceforge-img.svg
|   |   |   |   |   |-- student.png
|   |   |   |   |   |-- students-icon.svg
|   |   |   |   |   |-- subjects.png
|   |   |   |   |   \-- transportation-icon.svg
|   |   |   |   |-- img
|   |   |   |   |   |-- faculty_1.jpg
|   |   |   |   |   |-- faculty_10.jpg
|   |   |   |   |   |-- faculty_11.jpg
|   |   |   |   |   |-- faculty_12.jpg
|   |   |   |   |   |-- faculty_13.jpg
|   |   |   |   |   |-- faculty_14.jpg
|   |   |   |   |   |-- faculty_15.jpg
|   |   |   |   |   |-- faculty_2.jpg
|   |   |   |   |   |-- faculty_3.jpg
|   |   |   |   |   |-- faculty_4.jpg
|   |   |   |   |   |-- faculty_5.jpg
|   |   |   |   |   |-- faculty_6.jpg
|   |   |   |   |   |-- faculty_7.jpg
|   |   |   |   |   |-- faculty_8.jpg
|   |   |   |   |   |-- faculty_9.jpg
|   |   |   |   |   |-- student_1.jpg
|   |   |   |   |   |-- student_10.jpg
|   |   |   |   |   |-- student_11.jpg
|   |   |   |   |   |-- student_12.jpg
|   |   |   |   |   |-- student_13.jpg
|   |   |   |   |   |-- student_14.jpg
|   |   |   |   |   |-- student_15.jpg
|   |   |   |   |   |-- student_16.jpg
|   |   |   |   |   |-- student_17.jpg
|   |   |   |   |   |-- student_18.jpg
|   |   |   |   |   |-- student_19.jpg
|   |   |   |   |   |-- student_2.jpg
|   |   |   |   |   |-- student_20.jpg
|   |   |   |   |   |-- student_21.jpg
|   |   |   |   |   |-- student_22.jpg
|   |   |   |   |   |-- student_23.jpg
|   |   |   |   |   |-- student_24.jpg
|   |   |   |   |   |-- student_25.jpg
|   |   |   |   |   |-- student_3.jpg
|   |   |   |   |   |-- student_4.jpg
|   |   |   |   |   |-- student_5.jpg
|   |   |   |   |   |-- student_6.jpg
|   |   |   |   |   |-- student_7.jpg
|   |   |   |   |   |-- student_8.jpg
|   |   |   |   |   \-- student_9.jpg
|   |   |   |   |-- src
|   |   |   |   |   |-- img
|   |   |   |   |   |   |-- banner.jpg
|   |   |   |   |   |   |-- g2.webp
|   |   |   |   |   |   |-- openeducat_favicon.ico
|   |   |   |   |   |   |-- openeducat_logo.png
|   |   |   |   |   |   \-- openeducat_logo_demo.png
|   |   |   |   |   |-- js
|   |   |   |   |   |   |-- dashboard_ext.js
|   |   |   |   |   |   |-- field_inline_char.js
|   |   |   |   |   |   |-- g2_review.js
|   |   |   |   |   |   \-- inline_many2one.js
|   |   |   |   |   |-- scss
|   |   |   |   |   |   |-- base.scss
|   |   |   |   |   |   |-- main.scss
|   |   |   |   |   |   \-- style.scss
|   |   |   |   |   \-- xml
|   |   |   |   |       |-- base.xml
|   |   |   |   |       |-- dashboard_ext_openeducat.xml
|   |   |   |   |       |-- review.xml
|   |   |   |   |       \-- web_client.xml
|   |   |   |   \-- xls
|   |   |   |       |-- op_batch.xls
|   |   |   |       |-- op_course.xls
|   |   |   |       |-- op_faculty.xls
|   |   |   |       |-- op_student.xls
|   |   |   |       |-- op_student_course.xls
|   |   |   |       |-- op_subject.xls
|   |   |   |       \-- res_partner.xls
|   |   |   |-- tests
|   |   |   |   |-- __init__.py
|   |   |   |   |-- test_core.py
|   |   |   |   \-- test_core_common.py
|   |   |   |-- views
|   |   |   |   |-- batch_view.xml
|   |   |   |   |-- category_view.xml
|   |   |   |   |-- course_view.xml
|   |   |   |   |-- department_view.xml
|   |   |   |   |-- faculty_view.xml
|   |   |   |   |-- hr_view.xml
|   |   |   |   |-- op_academic_term_view.xml
|   |   |   |   |-- op_academic_year_view.xml
|   |   |   |   |-- program_level.xml
|   |   |   |   |-- program_view.xml
|   |   |   |   |-- res_company_view.xml
|   |   |   |   |-- res_config_setting_view.xml
|   |   |   |   |-- student_course_view.xml
|   |   |   |   |-- student_portal_view.xml
|   |   |   |   |-- student_view.xml
|   |   |   |   |-- subject_registration_view.xml
|   |   |   |   |-- subject_view.xml
|   |   |   |   \-- website_assets.xml
|   |   |   |-- wizard
|   |   |   |   |-- __init__.py
|   |   |   |   |-- bonafide_certificate_wizard.py
|   |   |   |   |-- bonafide_certificate_wizard_view.xml
|   |   |   |   |-- faculty_create_employee_wizard.py
|   |   |   |   |-- faculty_create_employee_wizard_view.xml
|   |   |   |   |-- faculty_create_user_wizard.py
|   |   |   |   |-- faculty_create_user_wizard_view.xml
|   |   |   |   |-- students_create_user_wizard.py
|   |   |   |   \-- students_create_user_wizard_view.xml
|   |   |   |-- __init__.py
|   |   |   |-- __manifest__.py
|   |   |   \-- README.rst
|   |   |-- openeducat_erp
|   |   |   |-- doc
|   |   |   |   \-- changelog.rst
|   |   |   |-- static
|   |   |   |   \-- description
|   |   |   |       |-- assignment-annotation-icon.png
|   |   |   |       |-- assignment.png
|   |   |   |       |-- attendance.png
|   |   |   |       |-- blog.png
|   |   |   |       |-- campus-icon.svg
|   |   |   |       |-- class.png
|   |   |   |       |-- courses-icon 1.svg
|   |   |   |       |-- dashboard.png
|   |   |   |       |-- enrollment.png
|   |   |   |       |-- events.png
|   |   |   |       |-- exam.png
|   |   |   |       |-- faculties-icon.svg
|   |   |   |       |-- faculty.png
|   |   |   |       |-- fees.svg
|   |   |   |       |-- financial.png
|   |   |   |       |-- g-2-img.png
|   |   |   |       |-- g2-img.svg
|   |   |   |       |-- grade-book-icon.svg
|   |   |   |       |-- help.jpg
|   |   |   |       |-- hr.png
|   |   |   |       |-- icon.png
|   |   |   |       |-- index.html
|   |   |   |       |-- inventory.svg
|   |   |   |       |-- kpi-dashboard-icon.svg
|   |   |   |       |-- lms-icon.svg
|   |   |   |       |-- media.png
|   |   |   |       |-- news.png
|   |   |   |       |-- news.svg
|   |   |   |       |-- notice-board-icon.svg
|   |   |   |       |-- openeducat-erp_banner.jpg
|   |   |   |       |-- openeducat-video-banner.jpg
|   |   |   |       |-- openeducat_account_financial_reports.svg
|   |   |   |       |-- openeducat_admission.svg
|   |   |   |       |-- openeducat_alumni_enterprise.svg
|   |   |   |       |-- openeducat_assignment.svg
|   |   |   |       |-- openeducat_attendance.svg
|   |   |   |       |-- openeducat_classroom.svg
|   |   |   |       |-- openeducat_erp_banner.jpg
|   |   |   |       |-- openeducat_exam.svg
|   |   |   |       |-- openeducat_library.svg
|   |   |   |       |-- openeducat_logo.png
|   |   |   |       |-- openeducat_timetable.svg
|   |   |   |       |-- reporting.png
|   |   |   |       |-- result.png
|   |   |   |       |-- session.png
|   |   |   |       |-- sis-icon.svg
|   |   |   |       |-- sourceforge-img.svg
|   |   |   |       |-- student.png
|   |   |   |       |-- students-icon.svg
|   |   |   |       \-- transportation-icon.svg
|   |   |   |-- __init__.py
|   |   |   |-- __manifest__.py
|   |   |   \-- README.rst
|   |   |-- openeducat_exam
|   |   |   |-- demo
|   |   |   |   |-- exam_attendees_demo.xml
|   |   |   |   |-- exam_demo.xml
|   |   |   |   |-- exam_room_demo.xml
|   |   |   |   |-- exam_session_demo.xml
|   |   |   |   |-- exam_type_demo.xml
|   |   |   |   |-- grade_configuration_demo.xml
|   |   |   |   |-- marksheet_line_demo.xml
|   |   |   |   |-- marksheet_register_demo.xml
|   |   |   |   |-- result_line_demo.xml
|   |   |   |   \-- result_template_demo.xml
|   |   |   |-- i18n
|   |   |   |   |-- ar_001.po
|   |   |   |   |-- da_DK.po
|   |   |   |   |-- de.po
|   |   |   |   |-- es.po
|   |   |   |   |-- fa.po
|   |   |   |   |-- fr.po
|   |   |   |   |-- id.po
|   |   |   |   |-- it.po
|   |   |   |   |-- lt.po
|   |   |   |   |-- nl.po
|   |   |   |   |-- openeducat_exam.pot
|   |   |   |   |-- pt.po
|   |   |   |   |-- ru.po
|   |   |   |   |-- th.po
|   |   |   |   |-- vi.po
|   |   |   |   |-- vi_VN.po
|   |   |   |   |-- zh_CN.po
|   |   |   |   \-- zh_HK.po
|   |   |   |-- menus
|   |   |   |   \-- op_menu.xml
|   |   |   |-- models
|   |   |   |   |-- __init__.py
|   |   |   |   |-- exam.py
|   |   |   |   |-- exam_attendees.py
|   |   |   |   |-- exam_room.py
|   |   |   |   |-- exam_session.py
|   |   |   |   |-- exam_type.py
|   |   |   |   |-- grade_configuration.py
|   |   |   |   |-- marksheet_line.py
|   |   |   |   |-- marksheet_register.py
|   |   |   |   |-- res_partner.py
|   |   |   |   |-- result_line.py
|   |   |   |   \-- result_template.py
|   |   |   |-- report
|   |   |   |   |-- __init__.py
|   |   |   |   |-- report_menu.xml
|   |   |   |   |-- report_ticket.xml
|   |   |   |   |-- student_hall_ticket_report.py
|   |   |   |   |-- student_marksheet.py
|   |   |   |   \-- student_marksheet.xml
|   |   |   |-- security
|   |   |   |   |-- ir.model.access.csv
|   |   |   |   \-- op_security.xml
|   |   |   |-- static
|   |   |   |   \-- description
|   |   |   |       |-- assignment-annotation-icon.png
|   |   |   |       |-- campus-icon.svg
|   |   |   |       |-- courses-icon 1.svg
|   |   |   |       |-- exam.png
|   |   |   |       |-- exam_session.png
|   |   |   |       |-- faculties-icon.svg
|   |   |   |       |-- fees.svg
|   |   |   |       |-- g-2-img.png
|   |   |   |       |-- g2-img.svg
|   |   |   |       |-- grade-book-icon.svg
|   |   |   |       |-- help.jpg
|   |   |   |       |-- hr.png
|   |   |   |       |-- icon.png
|   |   |   |       |-- index.html
|   |   |   |       |-- inventory.svg
|   |   |   |       |-- kpi-dashboard-icon.svg
|   |   |   |       |-- lms-icon.svg
|   |   |   |       |-- news.svg
|   |   |   |       |-- notice-board-icon.svg
|   |   |   |       |-- openeducat-exam_banner.jpg
|   |   |   |       |-- openeducat_account_financial_reports.svg
|   |   |   |       |-- openeducat_admission.svg
|   |   |   |       |-- openeducat_alumni_enterprise.svg
|   |   |   |       |-- openeducat_assignment.svg
|   |   |   |       |-- openeducat_attendance.svg
|   |   |   |       |-- openeducat_classroom.svg
|   |   |   |       |-- openeducat_exam.svg
|   |   |   |       |-- openeducat_exam_banner.jpg
|   |   |   |       |-- openeducat_library.svg
|   |   |   |       |-- openeducat_logo.png
|   |   |   |       |-- openeducat_timetable.svg
|   |   |   |       |-- sis-icon.svg
|   |   |   |       |-- sourceforge-img.svg
|   |   |   |       |-- students-icon.svg
|   |   |   |       \-- transportation-icon.svg
|   |   |   |-- tests
|   |   |   |   |-- __init__.py
|   |   |   |   |-- test_exam.py
|   |   |   |   \-- test_exam_common.py
|   |   |   |-- views
|   |   |   |   |-- exam_attendees_view.xml
|   |   |   |   |-- exam_room_view.xml
|   |   |   |   |-- exam_session_view.xml
|   |   |   |   |-- exam_type_view.xml
|   |   |   |   |-- exam_view.xml
|   |   |   |   |-- grade_configuration_view.xml
|   |   |   |   |-- marksheet_line_view.xml
|   |   |   |   |-- marksheet_register_view.xml
|   |   |   |   |-- res_partner_view.xml
|   |   |   |   |-- result_line_view.xml
|   |   |   |   \-- result_template_view.xml
|   |   |   |-- wizard
|   |   |   |   |-- __init__.py
|   |   |   |   |-- held_exam.py
|   |   |   |   |-- held_exam_view.xml
|   |   |   |   |-- room_distribution.py
|   |   |   |   \-- room_distribution_view.xml
|   |   |   |-- __init__.py
|   |   |   |-- __manifest__.py
|   |   |   \-- README.rst
|   |   |-- openeducat_facility
|   |   |   |-- demo
|   |   |   |   \-- facility_demo.xml
|   |   |   |-- i18n
|   |   |   |   |-- ar_001.po
|   |   |   |   |-- da_DK.po
|   |   |   |   |-- de.po
|   |   |   |   |-- es.po
|   |   |   |   |-- fa.po
|   |   |   |   |-- fr.po
|   |   |   |   |-- id.po
|   |   |   |   |-- it.po
|   |   |   |   |-- lt.po
|   |   |   |   |-- nl.po
|   |   |   |   |-- openeducat_facility.pot
|   |   |   |   |-- pt.po
|   |   |   |   |-- ru.po
|   |   |   |   |-- th.po
|   |   |   |   |-- vi.po
|   |   |   |   |-- vi_VN.po
|   |   |   |   |-- zh_CN.po
|   |   |   |   \-- zh_HK.po
|   |   |   |-- menus
|   |   |   |   \-- op_menu.xml
|   |   |   |-- models
|   |   |   |   |-- __init__.py
|   |   |   |   |-- facility.py
|   |   |   |   \-- facility_line.py
|   |   |   |-- security
|   |   |   |   |-- ir.model.access.csv
|   |   |   |   \-- op_facility_security.xml
|   |   |   |-- static
|   |   |   |   \-- description
|   |   |   |       |-- assignment-annotation-icon.png
|   |   |   |       |-- campus-icon.svg
|   |   |   |       |-- courses-icon 1.svg
|   |   |   |       |-- facility.png
|   |   |   |       |-- faculties-icon.svg
|   |   |   |       |-- fees.svg
|   |   |   |       |-- g-2-img.png
|   |   |   |       |-- g2-img.svg
|   |   |   |       |-- grade-book-icon.svg
|   |   |   |       |-- help.jpg
|   |   |   |       |-- hr.png
|   |   |   |       |-- icon.png
|   |   |   |       |-- index.html
|   |   |   |       |-- inventory.svg
|   |   |   |       |-- kpi-dashboard-icon.svg
|   |   |   |       |-- lms-icon.svg
|   |   |   |       |-- news.svg
|   |   |   |       |-- notice-board-icon.svg
|   |   |   |       |-- openeducat-facility_banner.jpg
|   |   |   |       |-- openeducat_account_financial_reports.svg
|   |   |   |       |-- openeducat_admission.svg
|   |   |   |       |-- openeducat_alumni_enterprise.svg
|   |   |   |       |-- openeducat_assignment.svg
|   |   |   |       |-- openeducat_attendance.svg
|   |   |   |       |-- openeducat_classroom.svg
|   |   |   |       |-- openeducat_exam.svg
|   |   |   |       |-- openeducat_facility_banner.jpg
|   |   |   |       |-- openeducat_library.svg
|   |   |   |       |-- openeducat_logo.png
|   |   |   |       |-- openeducat_timetable.svg
|   |   |   |       |-- sis-icon.svg
|   |   |   |       |-- sourceforge-img.svg
|   |   |   |       |-- students-icon.svg
|   |   |   |       \-- transportation-icon.svg
|   |   |   |-- tests
|   |   |   |   |-- __init__.py
|   |   |   |   |-- test_facility.py
|   |   |   |   \-- test_facility_common.py
|   |   |   |-- views
|   |   |   |   |-- facility_line_view.xml
|   |   |   |   \-- facility_view.xml
|   |   |   |-- __init__.py
|   |   |   |-- __manifest__.py
|   |   |   \-- README.rst
|   |   |-- openeducat_fees
|   |   |   |-- demo
|   |   |   |   |-- course_demo.xml
|   |   |   |   |-- fees_element_line_demo.xml
|   |   |   |   |-- fees_terms_demo.xml
|   |   |   |   |-- fees_terms_line_demo.xml
|   |   |   |   |-- product_category_demo.xml
|   |   |   |   |-- product_demo.xml
|   |   |   |   \-- student_fees_details_demo.xml
|   |   |   |-- i18n
|   |   |   |   |-- ar_001.po
|   |   |   |   |-- da_DK.po
|   |   |   |   |-- de.po
|   |   |   |   |-- es.po
|   |   |   |   |-- fa.po
|   |   |   |   |-- fr.po
|   |   |   |   |-- id.po
|   |   |   |   |-- it.po
|   |   |   |   |-- lt.po
|   |   |   |   |-- nl.po
|   |   |   |   |-- openeducat_fees.pot
|   |   |   |   |-- pt.po
|   |   |   |   |-- ru.po
|   |   |   |   |-- th.po
|   |   |   |   |-- vi.po
|   |   |   |   |-- vi_VN.po
|   |   |   |   |-- zh_CN.po
|   |   |   |   |-- zh_HK.po
|   |   |   |   \-- zh_TW.po
|   |   |   |-- models
|   |   |   |   |-- __init__.py
|   |   |   |   |-- course.py
|   |   |   |   |-- fees_element.py
|   |   |   |   |-- fees_terms.py
|   |   |   |   \-- student.py
|   |   |   |-- report
|   |   |   |   |-- __init__.py
|   |   |   |   |-- fees_analysis_report.py
|   |   |   |   |-- fees_analysis_report_view.xml
|   |   |   |   \-- report_menu.xml
|   |   |   |-- security
|   |   |   |   |-- ir.model.access.csv
|   |   |   |   \-- op_security.xml
|   |   |   |-- static
|   |   |   |   |-- description
|   |   |   |   |   |-- assignment-annotation-icon.png
|   |   |   |   |   |-- campus-icon.svg
|   |   |   |   |   |-- courses-icon 1.svg
|   |   |   |   |   |-- faculties-icon.svg
|   |   |   |   |   |-- fees.svg
|   |   |   |   |   |-- financial.png
|   |   |   |   |   |-- g-2-img.png
|   |   |   |   |   |-- g2-img.svg
|   |   |   |   |   |-- grade-book-icon.svg
|   |   |   |   |   |-- help.jpg
|   |   |   |   |   |-- hr.png
|   |   |   |   |   |-- icon.png
|   |   |   |   |   |-- index.html
|   |   |   |   |   |-- inventory.svg
|   |   |   |   |   |-- kpi-dashboard-icon.svg
|   |   |   |   |   |-- lms-icon.svg
|   |   |   |   |   |-- news.svg
|   |   |   |   |   |-- notice-board-icon.svg
|   |   |   |   |   |-- openeducat-fees_banner.jpg
|   |   |   |   |   |-- openeducat_account_financial_reports.svg
|   |   |   |   |   |-- openeducat_admission.svg
|   |   |   |   |   |-- openeducat_alumni_enterprise.svg
|   |   |   |   |   |-- openeducat_assignment.svg
|   |   |   |   |   |-- openeducat_attendance.svg
|   |   |   |   |   |-- openeducat_classroom.svg
|   |   |   |   |   |-- openeducat_exam.svg
|   |   |   |   |   |-- openeducat_fees_banner.jpg
|   |   |   |   |   |-- openeducat_library.svg
|   |   |   |   |   |-- openeducat_logo.png
|   |   |   |   |   |-- openeducat_timetable.svg
|   |   |   |   |   |-- sis-icon.svg
|   |   |   |   |   |-- sourceforge-img.svg
|   |   |   |   |   |-- students-icon.svg
|   |   |   |   |   |-- term_type_1.svg
|   |   |   |   |   |-- term_type_2.svg
|   |   |   |   |   |-- term_type_3.svg
|   |   |   |   |   |-- term_type_4.svg
|   |   |   |   |   |-- term_type_5.svg
|   |   |   |   |   \-- transportation-icon.svg
|   |   |   |   \-- src
|   |   |   |       |-- js
|   |   |   |       |   |-- fees_term_widget.js
|   |   |   |       |   \-- page_list.js
|   |   |   |       \-- xml
|   |   |   |           \-- fees_term_widget_template.xml
|   |   |   |-- tests
|   |   |   |   |-- __init__.py
|   |   |   |   |-- test_fees.py
|   |   |   |   \-- test_fees_common.py
|   |   |   |-- views
|   |   |   |   |-- course_view.xml
|   |   |   |   |-- fees_element_view.xml
|   |   |   |   |-- fees_terms_view.xml
|   |   |   |   \-- student_view.xml
|   |   |   |-- wizard
|   |   |   |   |-- __init__.py
|   |   |   |   |-- fees_detail_report_wizard.py
|   |   |   |   |-- fees_detail_report_wizard_view.xml
|   |   |   |   |-- select_term_type.xml
|   |   |   |   \-- select_term_type_wizard.py
|   |   |   |-- __init__.py
|   |   |   |-- __manifest__.py
|   |   |   \-- README.rst
|   |   |-- openeducat_library
|   |   |   |-- data
|   |   |   |   |-- action_rule_data.xml
|   |   |   |   |-- custom_paperformat.xml
|   |   |   |   |-- media_queue_sequence.xml
|   |   |   |   \-- product_demo.xml
|   |   |   |-- demo
|   |   |   |   |-- author_demo.xml
|   |   |   |   |-- library_card_demo.xml
|   |   |   |   |-- library_card_type_demo.xml
|   |   |   |   |-- media_demo.xml
|   |   |   |   |-- media_movement_demo.xml
|   |   |   |   |-- media_purchase_demo.xml
|   |   |   |   |-- media_queue_demo.xml
|   |   |   |   |-- media_type_demo.xml
|   |   |   |   |-- media_unit_demo.xml
|   |   |   |   |-- publisher_demo.xml
|   |   |   |   |-- res_users_demo.xml
|   |   |   |   \-- tag_demo.xml
|   |   |   |-- i18n
|   |   |   |   |-- ar_001.po
|   |   |   |   |-- da_DK.po
|   |   |   |   |-- de.po
|   |   |   |   |-- es.po
|   |   |   |   |-- fa.po
|   |   |   |   |-- fr.po
|   |   |   |   |-- id.po
|   |   |   |   |-- it.po
|   |   |   |   |-- lt.po
|   |   |   |   |-- nl.po
|   |   |   |   |-- openeducat_library.pot
|   |   |   |   |-- pt.po
|   |   |   |   |-- ru.po
|   |   |   |   |-- th.po
|   |   |   |   |-- vi.po
|   |   |   |   |-- vi_VN.po
|   |   |   |   |-- zh_CN.po
|   |   |   |   \-- zh_HK.po
|   |   |   |-- menus
|   |   |   |   \-- op_menu.xml
|   |   |   |-- models
|   |   |   |   |-- __init__.py
|   |   |   |   |-- account_invoice.py
|   |   |   |   |-- author.py
|   |   |   |   |-- faculty.py
|   |   |   |   |-- library.py
|   |   |   |   |-- media.py
|   |   |   |   |-- media_movement.py
|   |   |   |   |-- media_purchase.py
|   |   |   |   |-- media_queue.py
|   |   |   |   |-- media_type.py
|   |   |   |   |-- media_unit.py
|   |   |   |   |-- publisher.py
|   |   |   |   |-- student.py
|   |   |   |   \-- tag.py
|   |   |   |-- report
|   |   |   |   |-- __init__.py
|   |   |   |   |-- report_library_card_barcode.py
|   |   |   |   |-- report_library_card_barcode.xml
|   |   |   |   |-- report_media_barcode.py
|   |   |   |   |-- report_media_barcode.xml
|   |   |   |   |-- report_menu.xml
|   |   |   |   \-- report_student_library_card.xml
|   |   |   |-- security
|   |   |   |   |-- ir.model.access.csv
|   |   |   |   \-- op_security.xml
|   |   |   |-- static
|   |   |   |   \-- description
|   |   |   |       |-- assignment-annotation-icon.png
|   |   |   |       |-- authors.png
|   |   |   |       |-- campus-icon.svg
|   |   |   |       |-- courses-icon 1.svg
|   |   |   |       |-- faculties-icon.svg
|   |   |   |       |-- fees.svg
|   |   |   |       |-- g-2-img.png
|   |   |   |       |-- g2-img.svg
|   |   |   |       |-- grade-book-icon.svg
|   |   |   |       |-- help.jpg
|   |   |   |       |-- hr.png
|   |   |   |       |-- icon.png
|   |   |   |       |-- index.html
|   |   |   |       |-- inventory.svg
|   |   |   |       |-- kpi-dashboard-icon.svg
|   |   |   |       |-- lms-icon.svg
|   |   |   |       |-- media.png
|   |   |   |       |-- media_movements.png
|   |   |   |       |-- media_queue_request.png
|   |   |   |       |-- media_unit.png
|   |   |   |       |-- news.svg
|   |   |   |       |-- notice-board-icon.svg
|   |   |   |       |-- openeducat-library_banner.jpg
|   |   |   |       |-- openeducat_account_financial_reports.svg
|   |   |   |       |-- openeducat_admission.svg
|   |   |   |       |-- openeducat_alumni_enterprise.svg
|   |   |   |       |-- openeducat_assignment.svg
|   |   |   |       |-- openeducat_attendance.svg
|   |   |   |       |-- openeducat_classroom.svg
|   |   |   |       |-- openeducat_exam.svg
|   |   |   |       |-- openeducat_library.svg
|   |   |   |       |-- openeducat_library_banner.jpg
|   |   |   |       |-- openeducat_logo.png
|   |   |   |       |-- openeducat_timetable.svg
|   |   |   |       |-- publisher.png
|   |   |   |       |-- sis-icon.svg
|   |   |   |       |-- sourceforge-img.svg
|   |   |   |       |-- students-icon.svg
|   |   |   |       \-- transportation-icon.svg
|   |   |   |-- tests
|   |   |   |   |-- __init__.py
|   |   |   |   |-- test_library.py
|   |   |   |   \-- test_library_common.py
|   |   |   |-- views
|   |   |   |   |-- author_view.xml
|   |   |   |   |-- faculty_view.xml
|   |   |   |   |-- library_view.xml
|   |   |   |   |-- media_movement_view.xml
|   |   |   |   |-- media_purchase_view.xml
|   |   |   |   |-- media_queue_view.xml
|   |   |   |   |-- media_type_view.xml
|   |   |   |   |-- media_unit_view.xml
|   |   |   |   |-- media_view.xml
|   |   |   |   |-- publisher_view.xml
|   |   |   |   |-- student_view.xml
|   |   |   |   \-- tag_view.xml
|   |   |   |-- wizards
|   |   |   |   |-- __init__.py
|   |   |   |   |-- issue_media.py
|   |   |   |   |-- issue_media_view.xml
|   |   |   |   |-- reserve_media.py
|   |   |   |   |-- reserve_media_view.xml
|   |   |   |   |-- return_media.py
|   |   |   |   \-- return_media_view.xml
|   |   |   |-- __init__.py
|   |   |   |-- __manifest__.py
|   |   |   \-- README.rst
|   |   |-- openeducat_parent
|   |   |   |-- data
|   |   |   |   \-- parent_user_data.xml
|   |   |   |-- demo
|   |   |   |   |-- parent_demo.xml
|   |   |   |   |-- parent_relationship_demo.xml
|   |   |   |   |-- res_partner_demo.xml
|   |   |   |   \-- res_users_demo.xml
|   |   |   |-- i18n
|   |   |   |   |-- ar_001.po
|   |   |   |   |-- da_DK.po
|   |   |   |   |-- de.po
|   |   |   |   |-- es.po
|   |   |   |   |-- fa.po
|   |   |   |   |-- fr.po
|   |   |   |   |-- id.po
|   |   |   |   |-- it.po
|   |   |   |   |-- lt.po
|   |   |   |   |-- nl.po
|   |   |   |   |-- openeducat_parent.pot
|   |   |   |   |-- pt.po
|   |   |   |   |-- ru.po
|   |   |   |   |-- th.po
|   |   |   |   |-- vi.po
|   |   |   |   |-- zh.po
|   |   |   |   |-- zh_CN.po
|   |   |   |   \-- zh_HK.po
|   |   |   |-- menus
|   |   |   |   \-- op_menu.xml
|   |   |   |-- models
|   |   |   |   |-- __init__.py
|   |   |   |   |-- parent.py
|   |   |   |   \-- parent_relationship.py
|   |   |   |-- report
|   |   |   |   \-- report_student_bonafide_inherit.xml
|   |   |   |-- security
|   |   |   |   |-- ir.model.access.csv
|   |   |   |   \-- op_security.xml
|   |   |   |-- static
|   |   |   |   |-- description
|   |   |   |   |   |-- assignment-annotation-icon.png
|   |   |   |   |   |-- campus-icon.svg
|   |   |   |   |   |-- courses-icon 1.svg
|   |   |   |   |   |-- faculties-icon.svg
|   |   |   |   |   |-- fees.svg
|   |   |   |   |   |-- g-2-img.png
|   |   |   |   |   |-- g2-img.svg
|   |   |   |   |   |-- grade-book-icon.svg
|   |   |   |   |   |-- help.jpg
|   |   |   |   |   |-- hr.png
|   |   |   |   |   |-- icon.png
|   |   |   |   |   |-- index.html
|   |   |   |   |   |-- inventory.svg
|   |   |   |   |   |-- kpi-dashboard-icon.svg
|   |   |   |   |   |-- lms-icon.svg
|   |   |   |   |   |-- news.svg
|   |   |   |   |   |-- notice-board-icon.svg
|   |   |   |   |   |-- openeducat-parent_banner.jpg
|   |   |   |   |   |-- openeducat_account_financial_reports.svg
|   |   |   |   |   |-- openeducat_admission.svg
|   |   |   |   |   |-- openeducat_alumni_enterprise.svg
|   |   |   |   |   |-- openeducat_assignment.svg
|   |   |   |   |   |-- openeducat_attendance.svg
|   |   |   |   |   |-- openeducat_classroom.svg
|   |   |   |   |   |-- openeducat_exam.svg
|   |   |   |   |   |-- openeducat_library.svg
|   |   |   |   |   |-- openeducat_logo.png
|   |   |   |   |   |-- openeducat_parent_banner.jpg
|   |   |   |   |   |-- openeducat_timetable.svg
|   |   |   |   |   |-- parent.png
|   |   |   |   |   |-- sis-icon.svg
|   |   |   |   |   |-- sourceforge-img.svg
|   |   |   |   |   |-- students-icon.svg
|   |   |   |   |   \-- transportation-icon.svg
|   |   |   |   \-- xls
|   |   |   |       \-- op_parent.xls
|   |   |   |-- tests
|   |   |   |   |-- __init__.py
|   |   |   |   |-- test_parent.py
|   |   |   |   \-- test_parent_common.py
|   |   |   |-- views
|   |   |   |   |-- parent_relationship_view.xml
|   |   |   |   \-- parent_view.xml
|   |   |   |-- __init__.py
|   |   |   |-- __manifest__.py
|   |   |   \-- README.rst
|   |   |-- openeducat_timetable
|   |   |   |-- demo
|   |   |   |   |-- op_timetable_demo.xml
|   |   |   |   \-- timing_demo.xml
|   |   |   |-- i18n
|   |   |   |   |-- ar_001.po
|   |   |   |   |-- da_DK.po
|   |   |   |   |-- de.po
|   |   |   |   |-- es.po
|   |   |   |   |-- fa.po
|   |   |   |   |-- fr.po
|   |   |   |   |-- id.po
|   |   |   |   |-- it.po
|   |   |   |   |-- lt.po
|   |   |   |   |-- nl.po
|   |   |   |   |-- openeducat_timetable.pot
|   |   |   |   |-- pt.po
|   |   |   |   |-- ru.po
|   |   |   |   |-- th.po
|   |   |   |   |-- vi.po
|   |   |   |   |-- vi_VN.po
|   |   |   |   |-- zh_CN.po
|   |   |   |   \-- zh_HK.po
|   |   |   |-- menus
|   |   |   |   \-- op_menu.xml
|   |   |   |-- models
|   |   |   |   |-- __init__.py
|   |   |   |   |-- faculty.py
|   |   |   |   |-- res_config_setting.py
|   |   |   |   |-- timetable.py
|   |   |   |   \-- timing.py
|   |   |   |-- report
|   |   |   |   |-- __init__.py
|   |   |   |   |-- report_menu.xml
|   |   |   |   |-- report_timetable_student_generate.xml
|   |   |   |   |-- report_timetable_teacher_generate.xml
|   |   |   |   |-- timetable_report_student.py
|   |   |   |   \-- timetable_report_teacher.py
|   |   |   |-- security
|   |   |   |   |-- ir.model.access.csv
|   |   |   |   \-- op_security.xml
|   |   |   |-- static
|   |   |   |   |-- description
|   |   |   |   |   |-- assignment-annotation-icon.png
|   |   |   |   |   |-- campus-icon.svg
|   |   |   |   |   |-- courses-icon 1.svg
|   |   |   |   |   |-- faculties-icon.svg
|   |   |   |   |   |-- fees.svg
|   |   |   |   |   |-- g-2-img.png
|   |   |   |   |   |-- g2-img.svg
|   |   |   |   |   |-- generate_session.png
|   |   |   |   |   |-- grade-book-icon.svg
|   |   |   |   |   |-- help.jpg
|   |   |   |   |   |-- hr.png
|   |   |   |   |   |-- icon.png
|   |   |   |   |   |-- index.html
|   |   |   |   |   |-- inventory.svg
|   |   |   |   |   |-- kpi-dashboard-icon.svg
|   |   |   |   |   |-- lms-icon.svg
|   |   |   |   |   |-- news.svg
|   |   |   |   |   |-- notice-board-icon.svg
|   |   |   |   |   |-- openeducat-timetable_banner.jpg
|   |   |   |   |   |-- openeducat_account_financial_reports.svg
|   |   |   |   |   |-- openeducat_admission.svg
|   |   |   |   |   |-- openeducat_alumni_enterprise.svg
|   |   |   |   |   |-- openeducat_assignment.svg
|   |   |   |   |   |-- openeducat_attendance.svg
|   |   |   |   |   |-- openeducat_classroom.svg
|   |   |   |   |   |-- openeducat_exam.svg
|   |   |   |   |   |-- openeducat_library.svg
|   |   |   |   |   |-- openeducat_logo.png
|   |   |   |   |   |-- openeducat_timetable.svg
|   |   |   |   |   |-- openeducat_timetable_banner.jpg
|   |   |   |   |   |-- session.png
|   |   |   |   |   |-- sis-icon.svg
|   |   |   |   |   |-- sourceforge-img.svg
|   |   |   |   |   |-- students-icon.svg
|   |   |   |   |   |-- timing.png
|   |   |   |   |   \-- transportation-icon.svg
|   |   |   |   \-- xls
|   |   |   |       \-- op_session.xls
|   |   |   |-- tests
|   |   |   |   |-- __init__.py
|   |   |   |   |-- test_timetable.py
|   |   |   |   \-- test_timetable_common.py
|   |   |   |-- views
|   |   |   |   |-- faculty_view.xml
|   |   |   |   |-- res_config_setting_view.xml
|   |   |   |   |-- timetable_templates.xml
|   |   |   |   |-- timetable_view.xml
|   |   |   |   \-- timing_view.xml
|   |   |   |-- wizard
|   |   |   |   |-- __init__.py
|   |   |   |   |-- generate_timetable.py
|   |   |   |   |-- generate_timetable_view.xml
|   |   |   |   |-- session_confirmation.py
|   |   |   |   |-- session_confirmation.xml
|   |   |   |   |-- time_table_report.py
|   |   |   |   \-- time_table_report.xml
|   |   |   |-- __init__.py
|   |   |   |-- __manifest__.py
|   |   |   \-- README.rst
|   |   |-- theme_web_openeducat
|   |   |   |-- static
|   |   |   |   |-- description
|   |   |   |   |   |-- assignment-annotation-icon.png
|   |   |   |   |   |-- campus-icon.svg
|   |   |   |   |   |-- courses-icon 1.svg
|   |   |   |   |   |-- faculties-icon.svg
|   |   |   |   |   |-- fees.svg
|   |   |   |   |   |-- g-2-img.png
|   |   |   |   |   |-- g2-img.svg
|   |   |   |   |   |-- grade-book-icon.svg
|   |   |   |   |   |-- help.jpg
|   |   |   |   |   |-- hr.png
|   |   |   |   |   |-- icon.jpg
|   |   |   |   |   |-- icon.png
|   |   |   |   |   |-- icon_faculty.png
|   |   |   |   |   |-- icon_student.png
|   |   |   |   |   |-- index.html
|   |   |   |   |   |-- inventory.svg
|   |   |   |   |   |-- kpi-dashboard-icon.svg
|   |   |   |   |   |-- lms-icon.svg
|   |   |   |   |   |-- news.svg
|   |   |   |   |   |-- notice-board-icon.svg
|   |   |   |   |   |-- openeducat_account_financial_reports.svg
|   |   |   |   |   |-- openeducat_admission.svg
|   |   |   |   |   |-- openeducat_alumni_enterprise.svg
|   |   |   |   |   |-- openeducat_assignment.svg
|   |   |   |   |   |-- openeducat_attendance.svg
|   |   |   |   |   |-- openeducat_classroom.svg
|   |   |   |   |   |-- openeducat_exam.svg
|   |   |   |   |   |-- openeducat_library.svg
|   |   |   |   |   |-- openeducat_logo.png
|   |   |   |   |   |-- openeducat_timetable.svg
|   |   |   |   |   |-- sis-icon.svg
|   |   |   |   |   |-- sis.png
|   |   |   |   |   |-- sourceforge-img.svg
|   |   |   |   |   |-- students-icon.svg
|   |   |   |   |   |-- theme_full_page.png
|   |   |   |   |   |-- theme_web_openeducat_cover.jpg
|   |   |   |   |   |-- theme_web_openeducat_screenshot.jpg
|   |   |   |   |   \-- transportation-icon.svg
|   |   |   |   \-- src
|   |   |   |       |-- img
|   |   |   |       |   \-- banner
|   |   |   |       |       |-- about-01.png
|   |   |   |       |       |-- about-02.png
|   |   |   |       |       |-- about-03.png
|   |   |   |       |       |-- blog-card-01.jpg
|   |   |   |       |       |-- blog-card-02.jpg
|   |   |   |       |       |-- blog-card-03.jpg
|   |   |   |       |       |-- blog-card-04.jpg
|   |   |   |       |       |-- books.svg
|   |   |   |       |       |-- course-01-min.jpg
|   |   |   |       |       |-- course-02-min.jpg
|   |   |   |       |       |-- course-03-min.jpg
|   |   |   |       |       |-- course-thumb-2-min.jpg
|   |   |   |       |       |-- course-thumb-3-min.jpg
|   |   |   |       |       |-- course-thumb-6-min.jpg
|   |   |   |       |       |-- dictionary.svg
|   |   |   |       |       |-- dots.png
|   |   |   |       |       |-- education-01.png
|   |   |   |       |       |-- facebook.png
|   |   |   |       |       |-- financial-analysis.svg
|   |   |   |       |       |-- google.png
|   |   |   |       |       |-- graduating-student-01.png
|   |   |   |       |       |-- passed.svg
|   |   |   |       |       |-- registration.svg
|   |   |   |       |       |-- speak.svg
|   |   |   |       |       |-- student-img.png
|   |   |   |       |       |-- student.svg
|   |   |   |       |       |-- teacher.svg
|   |   |   |       |       |-- team-01.jpg
|   |   |   |       |       |-- team-01.png
|   |   |   |       |       |-- team-02.jpg
|   |   |   |       |       |-- team-03.jpg
|   |   |   |       |       |-- team-04.jpg
|   |   |   |       |       |-- team-05.jpg
|   |   |   |       |       |-- team-06.jpg
|   |   |   |       |       |-- trophy-01.png
|   |   |   |       |       \-- video-01.jpg
|   |   |   |       |-- js
|   |   |   |       |   \-- home.js
|   |   |   |       \-- scss
|   |   |   |           |-- primary_variables.scss
|   |   |   |           \-- style.scss
|   |   |   |-- views
|   |   |   |   \-- homepage.xml
|   |   |   |-- __init__.py
|   |   |   \-- __manifest__.py
|   |   |-- .coveragerc
|   |   |-- .gitattributes
|   |   |-- .gitignore
|   |   |-- .pre-commit-config.yaml
|   |   |-- cfg_run_flake8.cfg
|   |   |-- cfg_run_pylint.cfg
|   |   |-- LICENSE
|   |   \-- README.md
|   |-- private-gpt
|   |   |-- .docker
|   |   |   \-- router.yml
|   |   |-- .github
|   |   |   |-- ISSUE_TEMPLATE
|   |   |   |   |-- bug.yml
|   |   |   |   |-- config.yml
|   |   |   |   |-- docs.yml
|   |   |   |   |-- feature.yml
|   |   |   |   \-- question.yml
|   |   |   |-- release_please
|   |   |   |   |-- .release-please-config.json
|   |   |   |   \-- .release-please-manifest.json
|   |   |   |-- workflows
|   |   |   |   |-- actions
|   |   |   |   |   \-- install_dependencies
|   |   |   |   |       \-- action.yml
|   |   |   |   |-- fern-check.yml
|   |   |   |   |-- generate-release.yml
|   |   |   |   |-- preview-docs.yml
|   |   |   |   |-- publish-docs.yml
|   |   |   |   |-- release-please.yml
|   |   |   |   |-- stale.yml
|   |   |   |   \-- tests.yml
|   |   |   \-- pull_request_template.md
|   |   |-- fern
|   |   |   |-- docs
|   |   |   |   |-- assets
|   |   |   |   |   |-- favicon.ico
|   |   |   |   |   |-- header.jpeg
|   |   |   |   |   |-- logo_dark.png
|   |   |   |   |   |-- logo_light.png
|   |   |   |   |   \-- ui.png
|   |   |   |   \-- pages
|   |   |   |       |-- api-reference
|   |   |   |       |   |-- api-reference.mdx
|   |   |   |       |   \-- sdks.mdx
|   |   |   |       |-- installation
|   |   |   |       |   |-- concepts.mdx
|   |   |   |       |   |-- installation.mdx
|   |   |   |       |   \-- troubleshooting.mdx
|   |   |   |       |-- manual
|   |   |   |       |   |-- ingestion-reset.mdx
|   |   |   |       |   |-- ingestion.mdx
|   |   |   |       |   |-- llms.mdx
|   |   |   |       |   |-- nodestore.mdx
|   |   |   |       |   |-- reranker.mdx
|   |   |   |       |   |-- settings.mdx
|   |   |   |       |   \-- vectordb.mdx
|   |   |   |       |-- overview
|   |   |   |       |   \-- welcome.mdx
|   |   |   |       |-- quickstart
|   |   |   |       |   \-- quickstart.mdx
|   |   |   |       |-- recipes
|   |   |   |       |   |-- quickstart.mdx
|   |   |   |       |   \-- summarize.mdx
|   |   |   |       \-- ui
|   |   |   |           |-- alternatives.mdx
|   |   |   |           \-- gradio.mdx
|   |   |   |-- openapi
|   |   |   |   \-- openapi.json
|   |   |   |-- docs.yml
|   |   |   |-- fern.config.json
|   |   |   |-- generators.yml
|   |   |   \-- README.md
|   |   |-- local_data
|   |   |   \-- .gitignore
|   |   |-- models
|   |   |   \-- .gitignore
|   |   |-- private_gpt
|   |   |   |-- components
|   |   |   |   |-- embedding
|   |   |   |   |   |-- custom
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- sagemaker.py
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- embedding_component.py
|   |   |   |   |-- ingest
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- ingest_component.py
|   |   |   |   |   \-- ingest_helper.py
|   |   |   |   |-- llm
|   |   |   |   |   |-- custom
|   |   |   |   |   |   |-- __init__.py
|   |   |   |   |   |   \-- sagemaker.py
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- llm_component.py
|   |   |   |   |   \-- prompt_helper.py
|   |   |   |   |-- node_store
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- node_store_component.py
|   |   |   |   |-- vector_store
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- batched_chroma.py
|   |   |   |   |   \-- vector_store_component.py
|   |   |   |   \-- __init__.py
|   |   |   |-- open_ai
|   |   |   |   |-- extensions
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- context_filter.py
|   |   |   |   |-- __init__.py
|   |   |   |   \-- openai_models.py
|   |   |   |-- server
|   |   |   |   |-- chat
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- chat_router.py
|   |   |   |   |   \-- chat_service.py
|   |   |   |   |-- chunks
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- chunks_router.py
|   |   |   |   |   \-- chunks_service.py
|   |   |   |   |-- completions
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- completions_router.py
|   |   |   |   |-- embeddings
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- embeddings_router.py
|   |   |   |   |   \-- embeddings_service.py
|   |   |   |   |-- health
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- health_router.py
|   |   |   |   |-- ingest
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   |-- ingest_router.py
|   |   |   |   |   |-- ingest_service.py
|   |   |   |   |   |-- ingest_watcher.py
|   |   |   |   |   \-- model.py
|   |   |   |   |-- recipes
|   |   |   |   |   \-- summarize
|   |   |   |   |       |-- __init__.py
|   |   |   |   |       |-- summarize_router.py
|   |   |   |   |       \-- summarize_service.py
|   |   |   |   |-- utils
|   |   |   |   |   |-- __init__.py
|   |   |   |   |   \-- auth.py
|   |   |   |   \-- __init__.py
|   |   |   |-- settings
|   |   |   |   |-- __init__.py
|   |   |   |   |-- settings.py
|   |   |   |   |-- settings_loader.py
|   |   |   |   \-- yaml.py
|   |   |   |-- ui
|   |   |   |   |-- __init__.py
|   |   |   |   |-- avatar-bot.ico
|   |   |   |   |-- images.py
|   |   |   |   \-- ui.py
|   |   |   |-- utils
|   |   |   |   |-- __init__.py
|   |   |   |   |-- eta.py
|   |   |   |   |-- ollama.py
|   |   |   |   |-- retry.py
|   |   |   |   \-- typing.py
|   |   |   |-- __init__.py
|   |   |   |-- __main__.py
|   |   |   |-- constants.py
|   |   |   |-- di.py
|   |   |   |-- launcher.py
|   |   |   |-- main.py
|   |   |   \-- paths.py
|   |   |-- scripts
|   |   |   |-- __init__.py
|   |   |   |-- extract_openapi.py
|   |   |   |-- ingest_folder.py
|   |   |   |-- setup
|   |   |   \-- utils.py
|   |   |-- tests
|   |   |   |-- fixtures
|   |   |   |   |-- __init__.py
|   |   |   |   |-- auto_close_qdrant.py
|   |   |   |   |-- fast_api_test_client.py
|   |   |   |   |-- ingest_helper.py
|   |   |   |   \-- mock_injector.py
|   |   |   |-- server
|   |   |   |   |-- chat
|   |   |   |   |   \-- test_chat_routes.py
|   |   |   |   |-- chunks
|   |   |   |   |   |-- chunk_test.txt
|   |   |   |   |   \-- test_chunk_routes.py
|   |   |   |   |-- embeddings
|   |   |   |   |   \-- test_embedding_routes.py
|   |   |   |   |-- ingest
|   |   |   |   |   |-- test.pdf
|   |   |   |   |   |-- test.txt
|   |   |   |   |   |-- test_ingest_routes.py
|   |   |   |   |   \-- test_local_ingest.py
|   |   |   |   |-- recipes
|   |   |   |   |   \-- test_summarize_router.py
|   |   |   |   \-- utils
|   |   |   |       |-- test_auth.py
|   |   |   |       \-- test_simple_auth.py
|   |   |   |-- settings
|   |   |   |   |-- test_settings.py
|   |   |   |   \-- test_settings_loader.py
|   |   |   |-- ui
|   |   |   |   \-- test_ui.py
|   |   |   |-- __init__.py
|   |   |   |-- conftest.py
|   |   |   \-- test_prompt_helper.py
|   |   |-- tiktoken_cache
|   |   |   \-- .gitignore
|   |   |-- .dockerignore
|   |   |-- .gitignore
|   |   |-- .pre-commit-config.yaml
|   |   |-- CHANGELOG.md
|   |   |-- CITATION.cff
|   |   |-- docker-compose.yaml
|   |   |-- Dockerfile.llamacpp-cpu
|   |   |-- Dockerfile.ollama
|   |   |-- LICENSE
|   |   |-- Makefile
|   |   |-- poetry.lock
|   |   |-- pyproject.toml
|   |   |-- README.md
|   |   |-- settings-azopenai.yaml
|   |   |-- settings-docker.yaml
|   |   |-- settings-gemini.yaml
|   |   |-- settings-local.yaml
|   |   |-- settings-mock.yaml
|   |   |-- settings-ollama-pg.yaml
|   |   |-- settings-ollama.yaml
|   |   |-- settings-openai.yaml
|   |   |-- settings-sagemaker.yaml
|   |   |-- settings-test.yaml
|   |   |-- settings-vllm.yaml
|   |   |-- settings.yaml
|   |   \-- version.txt
|   \-- saas-starter-kit
|       |-- .do
|       |   \-- deploy.template.yaml
|       |-- .github
|       |   |-- workflows
|       |   |   \-- main.yml
|       |   \-- dependabot.yml
|       |-- __tests__
|       |   \-- lib
|       |       \-- server-common.spec.ts
|       |-- components
|       |   |-- account
|       |   |   |-- index.ts
|       |   |   |-- ManageSessions.tsx
|       |   |   |-- UpdateAccount.tsx
|       |   |   |-- UpdateEmail.tsx
|       |   |   |-- UpdateName.tsx
|       |   |   |-- UpdatePassword.tsx
|       |   |   |-- UpdateTheme.tsx
|       |   |   \-- UploadAvatar.tsx
|       |   |-- apiKey
|       |   |   |-- APIKeys.tsx
|       |   |   |-- APIKeysContainer.tsx
|       |   |   \-- NewAPIKey.tsx
|       |   |-- auth
|       |   |   |-- AgreeMessage.tsx
|       |   |   |-- GithubButton.tsx
|       |   |   |-- GoogleButton.tsx
|       |   |   |-- index.ts
|       |   |   |-- Join.tsx
|       |   |   |-- JoinWithInvitation.tsx
|       |   |   |-- MagicLink.tsx
|       |   |   \-- ResetPassword.tsx
|       |   |-- billing
|       |   |   |-- Help.tsx
|       |   |   |-- LinkToPortal.tsx
|       |   |   |-- PaymentButton.tsx
|       |   |   |-- ProductPricing.tsx
|       |   |   \-- Subscriptions.tsx
|       |   |-- defaultLanding
|       |   |   |-- data
|       |   |   |   |-- faq.json
|       |   |   |   |-- features.json
|       |   |   |   \-- pricing.json
|       |   |   |-- FAQSection.tsx
|       |   |   |-- FeatureSection.tsx
|       |   |   |-- HeroSection.tsx
|       |   |   \-- PricingSection.tsx
|       |   |-- emailTemplates
|       |   |   |-- AccountLocked.tsx
|       |   |   |-- EmailLayout.tsx
|       |   |   |-- index.ts
|       |   |   |-- MagicLink.tsx
|       |   |   |-- ResetPassword.tsx
|       |   |   |-- TeamInvite.tsx
|       |   |   |-- VerificationEmail.tsx
|       |   |   \-- WelcomeEmail.tsx
|       |   |-- invitation
|       |   |   |-- AcceptInvitation.tsx
|       |   |   |-- EmailDomainMismatch.tsx
|       |   |   |-- EmailMismatch.tsx
|       |   |   |-- index.ts
|       |   |   |-- InviteMember.tsx
|       |   |   |-- InviteViaEmail.tsx
|       |   |   |-- InviteViaLink.tsx
|       |   |   |-- NotAuthenticated.tsx
|       |   |   \-- PendingInvitations.tsx
|       |   |-- layouts
|       |   |   |-- AccountLayout.tsx
|       |   |   |-- AuthLayout.tsx
|       |   |   \-- index.ts
|       |   |-- shared
|       |   |   |-- shell
|       |   |   |   |-- AppShell.tsx
|       |   |   |   |-- Brand.tsx
|       |   |   |   |-- Drawer.tsx
|       |   |   |   |-- Header.tsx
|       |   |   |   |-- Navigation.tsx
|       |   |   |   |-- NavigationItems.tsx
|       |   |   |   |-- ProductNavigation.tsx
|       |   |   |   |-- TeamNavigation.tsx
|       |   |   |   \-- UserNavigation.tsx
|       |   |   |-- table
|       |   |   |   |-- Table.tsx
|       |   |   |   |-- TableBody.tsx
|       |   |   |   \-- TableHeader.tsx
|       |   |   |-- AccessControl.tsx
|       |   |   |-- Alert.tsx
|       |   |   |-- Badge.tsx
|       |   |   |-- Card.tsx
|       |   |   |-- Checkbox.tsx
|       |   |   |-- ConfirmationDialog.tsx
|       |   |   |-- CopyToClipboardButton.tsx
|       |   |   |-- EmptyState.tsx
|       |   |   |-- Error.tsx
|       |   |   |-- GoogleReCAPTCHA.tsx
|       |   |   |-- index.ts
|       |   |   |-- InputWithCopyButton.tsx
|       |   |   |-- InputWithLabel.tsx
|       |   |   |-- LetterAvatar.tsx
|       |   |   |-- Loading.tsx
|       |   |   |-- Modal.tsx
|       |   |   |-- TeamDropdown.tsx
|       |   |   |-- TogglePasswordVisibility.tsx
|       |   |   \-- WithLoadingAndError.tsx
|       |   |-- team
|       |   |   |-- CreateTeam.tsx
|       |   |   |-- index.ts
|       |   |   |-- Members.tsx
|       |   |   |-- RemoveTeam.tsx
|       |   |   |-- Teams.tsx
|       |   |   |-- TeamSettings.tsx
|       |   |   |-- TeamTab.tsx
|       |   |   \-- UpdateMemberRole.tsx
|       |   |-- webhook
|       |   |   |-- CreateWebhook.tsx
|       |   |   |-- EditWebhook.tsx
|       |   |   |-- EventTypes.tsx
|       |   |   |-- Form.tsx
|       |   |   |-- index.ts
|       |   |   \-- Webhooks.tsx
|       |   \-- styles.ts
|       |-- hooks
|       |   |-- useAPIKeys.ts
|       |   |-- useCanAccess.ts
|       |   |-- useCustomSignout.ts
|       |   |-- useInvitation.ts
|       |   |-- useInvitations.ts
|       |   |-- usePermissions.ts
|       |   |-- useTeam.ts
|       |   |-- useTeamMembers.ts
|       |   |-- useTeams.ts
|       |   |-- useTheme.ts
|       |   |-- useWebhook.ts
|       |   \-- useWebhooks.ts
|       |-- lib
|       |   |-- email
|       |   |   |-- freeEmailService.json
|       |   |   |-- sendEmail.ts
|       |   |   |-- sendMagicLink.ts
|       |   |   |-- sendPasswordResetEmail.ts
|       |   |   |-- sendTeamInviteEmail.ts
|       |   |   |-- sendVerificationEmail.ts
|       |   |   |-- sendWelcomeEmail.ts
|       |   |   \-- utils.ts
|       |   |-- guards
|       |   |   |-- team-api-key.ts
|       |   |   |-- team-dsync.ts
|       |   |   \-- team-sso.ts
|       |   |-- jackson
|       |   |   |-- dsync
|       |   |   |   |-- embed.ts
|       |   |   |   |-- hosted.ts
|       |   |   |   |-- index.ts
|       |   |   |   \-- utils.ts
|       |   |   |-- sso
|       |   |   |   |-- embed.ts
|       |   |   |   |-- hosted.ts
|       |   |   |   |-- index.ts
|       |   |   |   \-- utils.ts
|       |   |   |-- config.ts
|       |   |   \-- dsyncEvents.ts
|       |   |-- zod
|       |   |   |-- index.ts
|       |   |   |-- primitives.ts
|       |   |   \-- schema.ts
|       |   |-- accountLock.ts
|       |   |-- app.ts
|       |   |-- auth.ts
|       |   |-- common.ts
|       |   |-- env.ts
|       |   |-- errors.ts
|       |   |-- fetcher.ts
|       |   |-- inferSSRProps.ts
|       |   |-- jackson.ts
|       |   |-- metrics.ts
|       |   |-- nextAuth.ts
|       |   |-- permissions.ts
|       |   |-- prisma.ts
|       |   |-- rbac.ts
|       |   |-- recaptcha.ts
|       |   |-- retraced.ts
|       |   |-- server-common.ts
|       |   |-- session.ts
|       |   |-- slack.ts
|       |   |-- stripe.ts
|       |   |-- svix.ts
|       |   \-- theme.ts
|       |-- locales
|       |   \-- en
|       |       \-- common.json
|       |-- models
|       |   |-- account.ts
|       |   |-- apiKey.ts
|       |   |-- invitation.ts
|       |   |-- passwordReset.ts
|       |   |-- price.ts
|       |   |-- service.ts
|       |   |-- session.ts
|       |   |-- subscription.ts
|       |   |-- team.ts
|       |   |-- teamMember.ts
|       |   |-- user.ts
|       |   \-- verificationToken.ts
|       |-- pages
|       |   |-- api
|       |   |   |-- auth
|       |   |   |   |-- sso
|       |   |   |   |   |-- acs.ts
|       |   |   |   |   \-- verify.ts
|       |   |   |   |-- [...nextauth].ts
|       |   |   |   |-- custom-signout.ts
|       |   |   |   |-- forgot-password.ts
|       |   |   |   |-- join.ts
|       |   |   |   |-- resend-email-token.ts
|       |   |   |   |-- reset-password.ts
|       |   |   |   \-- unlock-account.ts
|       |   |   |-- invitations
|       |   |   |   \-- [token].ts
|       |   |   |-- oauth
|       |   |   |   |-- authorize.ts
|       |   |   |   |-- oidc.ts
|       |   |   |   |-- saml.ts
|       |   |   |   |-- token.ts
|       |   |   |   \-- userinfo.ts
|       |   |   |-- scim
|       |   |   |   \-- v2.0
|       |   |   |       \-- [...directory].ts
|       |   |   |-- sessions
|       |   |   |   |-- [id].ts
|       |   |   |   \-- index.ts
|       |   |   |-- teams
|       |   |   |   |-- [slug]
|       |   |   |   |   |-- api-keys
|       |   |   |   |   |   |-- [apiKeyId].ts
|       |   |   |   |   |   \-- index.ts
|       |   |   |   |   |-- dsync
|       |   |   |   |   |   |-- [directoryId].ts
|       |   |   |   |   |   \-- index.ts
|       |   |   |   |   |-- payments
|       |   |   |   |   |   |-- create-checkout-session.ts
|       |   |   |   |   |   |-- create-portal-link.ts
|       |   |   |   |   |   \-- products.ts
|       |   |   |   |   |-- webhooks
|       |   |   |   |   |   |-- [endpointId].ts
|       |   |   |   |   |   \-- index.ts
|       |   |   |   |   |-- index.ts
|       |   |   |   |   |-- invitations.ts
|       |   |   |   |   |-- members.ts
|       |   |   |   |   |-- permissions.ts
|       |   |   |   |   \-- sso.ts
|       |   |   |   \-- index.ts
|       |   |   |-- webhooks
|       |   |   |   |-- dsync.ts
|       |   |   |   \-- stripe.ts
|       |   |   |-- well-known
|       |   |   |   \-- saml.cer.ts
|       |   |   |-- health.ts
|       |   |   |-- hello.ts
|       |   |   |-- idp.ts
|       |   |   |-- import-hack.ts
|       |   |   |-- password.ts
|       |   |   \-- users.ts
|       |   |-- auth
|       |   |   |-- reset-password
|       |   |   |   \-- [token].tsx
|       |   |   |-- sso
|       |   |   |   |-- idp-select.tsx
|       |   |   |   \-- index.tsx
|       |   |   |-- forgot-password.tsx
|       |   |   |-- idp-login.tsx
|       |   |   |-- join.tsx
|       |   |   |-- login.tsx
|       |   |   |-- magic-link.tsx
|       |   |   |-- resend-email-token.tsx
|       |   |   |-- unlock-account.tsx
|       |   |   |-- verify-email-token.tsx
|       |   |   \-- verify-email.tsx
|       |   |-- invitations
|       |   |   \-- [token].tsx
|       |   |-- settings
|       |   |   |-- account.tsx
|       |   |   \-- security.tsx
|       |   |-- teams
|       |   |   |-- [slug]
|       |   |   |   |-- api-keys.tsx
|       |   |   |   |-- audit-logs.tsx
|       |   |   |   |-- billing.tsx
|       |   |   |   |-- directory-sync.tsx
|       |   |   |   |-- members.tsx
|       |   |   |   |-- products.tsx
|       |   |   |   |-- settings.tsx
|       |   |   |   |-- sso.tsx
|       |   |   |   \-- webhooks.tsx
|       |   |   |-- index.tsx
|       |   |   \-- switch.tsx
|       |   |-- well-known
|       |   |   \-- saml-configuration.tsx
|       |   |-- 404.tsx
|       |   |-- 500.tsx
|       |   |-- _app.tsx
|       |   |-- _document.tsx
|       |   |-- dashboard.tsx
|       |   \-- index.tsx
|       |-- prisma
|       |   |-- migrations
|       |   |   |-- 20230625203909_init
|       |   |   |   \-- migration.sql
|       |   |   |-- 20230703084002_add_api_keys
|       |   |   |   \-- migration.sql
|       |   |   |-- 20230703084117_add_index_user
|       |   |   |   \-- migration.sql
|       |   |   |-- 20230720113226_make_password_optional
|       |   |   |   \-- migration.sql
|       |   |   |-- 20231109082527_add_account_lockout
|       |   |   |   \-- migration.sql
|       |   |   |-- 20240109041326_columns_for_invitation_link
|       |   |   |   \-- migration.sql
|       |   |   |-- 20240212105842_stripe
|       |   |   |   \-- migration.sql
|       |   |   |-- 20240213160517_indices
|       |   |   |   \-- migration.sql
|       |   |   |-- 20240226091046_add_jackson_schema
|       |   |   |   \-- migration.sql
|       |   |   |-- 20240316224800_add_index_billing_id
|       |   |   |   \-- migration.sql
|       |   |   |-- 20240531124127_expand_jackson_namespace_column
|       |   |   |   \-- migration.sql
|       |   |   \-- migration_lock.toml
|       |   |-- schema.prisma
|       |   \-- seed.ts
|       |-- public
|       |   |-- home-hero.svg
|       |   |-- logo.png
|       |   |-- logowhite.png
|       |   |-- saas-starter-kit-poster.png
|       |   |-- user-default-profile.jpeg
|       |   \-- vercel.svg
|       |-- styles
|       |   |-- globals.css
|       |   \-- sdk-override.module.css
|       |-- tests
|       |   \-- e2e
|       |       |-- auth
|       |       |   |-- idp-initiated.spec.ts
|       |       |   \-- sso.login.spec.ts
|       |       |-- session
|       |       |   \-- session.spec.ts
|       |       |-- settings
|       |       |   |-- api-key.spec.ts
|       |       |   |-- directory-sync.spec.ts
|       |       |   |-- members.spec.ts
|       |       |   \-- team-settings.spec.ts
|       |       \-- support
|       |           |-- fixtures
|       |           |   |-- api-keys-page.ts
|       |           |   |-- consts.ts
|       |           |   |-- directory-sync-page.ts
|       |           |   |-- index.ts
|       |           |   |-- join-page.ts
|       |           |   |-- login-page.ts
|       |           |   |-- member-page.ts
|       |           |   |-- security-page.ts
|       |           |   |-- settings-page.ts
|       |           |   \-- sso-page.ts
|       |           |-- utils
|       |           |   \-- throttling-network-presets.ts
|       |           |-- account.setup.ts
|       |           |-- account.teardown.ts
|       |           |-- globalSetup.ts
|       |           \-- helper.ts
|       |-- types
|       |   |-- base.ts
|       |   |-- index.ts
|       |   |-- next-auth.d.ts
|       |   \-- next.ts
|       |-- .env.example
|       |-- .gitignore
|       |-- .prettierignore
|       |-- .prettierrc.js
|       |-- .release-it.json
|       |-- app.json
|       |-- check-locale.js
|       |-- CODE_OF_CONDUCT.md
|       |-- CONTRIBUTING.md
|       |-- delete-team.js
|       |-- docker-compose.yml
|       |-- eslint.config.cjs
|       |-- find-dupe-locale.js
|       |-- i18next.d.ts
|       |-- instrumentation.ts
|       |-- jest.config.js
|       |-- jest.setup.js
|       |-- LICENSE
|       |-- middleware.ts
|       |-- next-env.d.ts
|       |-- next-i18next.config.js
|       |-- next.config.js
|       |-- package-lock.json
|       |-- package.json
|       |-- playwright.config.ts
|       |-- postcss.config.js
|       |-- Procfile
|       |-- README.md
|       |-- sentry.client.config.ts
|       |-- sync-stripe.js
|       |-- tailwind.config.js
|       \-- tsconfig.json
|-- scripts
|   |-- backup.sh
|   |-- production_readiness_gate.py
|   |-- run_backend_tests_lightweight.sh
|   \-- verify_restore.py
|-- uploads
|   |-- 2fe7c887-6748-4b5c-8845-f40f52dd65f3_ef4f92e7-7e0f-4916-950a-3c9a4e3c78cb_notes.pdf
|   |-- 442355d2-d6d7-4907-b208-aef794b2ced5_24c7059b-8a82-4e29-a259-61d234ec8e7d_notes.pdf
|   |-- 58a2a79e-f0b7-4bd3-a251-741144835538_279ee53b-5eb5-4ee4-ba0c-5d5e123ee36c_notes.pdf
|   |-- 720c31cc-f5b4-49ad-bfa6-736636dfc457_98cfd31f-d233-4c6e-b4f3-c9237e4864e1_notes.pdf
|   |-- bc301bff-8797-475f-a132-98969a70f04a_266dd753-d363-4cb4-8638-6493f8fb4247_notes.pdf
|   |-- befd27b8-bb1d-457c-aadd-93b79e4d8699_8af5ca18-c5e1-427b-95d2-0b4a2aaf1d67_notes.pdf
|   \-- d43e4bb5-e7de-4403-aa69-07bf89663cd9_1ac2cf38-2c8e-4337-b8c8-3d0e2ae11eef_notes.pdf
|-- .dockerignore
|-- .env.example
|-- .gitignore
|-- AI_STUDIO_IMPLEMENTATION_PLAN.md
|-- api_logs.txt
|-- backend-7125.log
|-- business_analysis.md
|-- CHANGELOG.md
|-- competitor_analysis_mastersoft.txt
|-- CONTRIBUTING.md
|-- CURRENT_WORK.md
|-- demo.bat
|-- demo.db
|-- demo.sh
|-- docker-compose.demo.yml
|-- docker-compose.yml
|-- Dockerfile.demo
|-- Dockerfile.production
|-- feature_guide.md
|-- How to Document a Website Project.md
|-- implementation_plan.md
|-- MULTI_TIER_ROLLOUT_PLAN.md
|-- nginx.conf
|-- nginx.demo.conf
|-- product_presentation.pdf
|-- production_readiness_report.md
|-- PRODUCTION_READY_PLAN.md
|-- pytest.ini
|-- README.md
|-- REMAINING_WORK.md
|-- scan_codebase.py
|-- SESSION_WALKTHROUGH.md
|-- STAR_FEATURES_ANALYSIS.md
|-- UX_REDIGN_PLAN.md
|-- VidyaOs_feature_guide.md
|-- VidyaOS_Features_List.md
\-- WHATSAPP_MIGRATION_PLAN.md
```

## Top-level Runtime / Data Directories

These directories exist in the workspace and are part of deployment/runtime shape, even when their internal contents are generated or environment-specific:

- `.qodo/`
- `MagicMock/`
- `compliance_exports/`
- `data/`
- `private_storage/`
- `raw/`
- `repo/`
- `uploads/`
- `vector_store/`

## Primary Source Roots

- `backend/` : FastAPI backend, domains, middleware, models, AI workflows, tests
- `frontend/` : Next.js app routes, shared UI, mascot UI, E2E tests
- `documentation/` : audits, plans, checklists, reports, architecture docs
- `scripts/` : project-level operational scripts
- `.github/` : CI/CD workflows
- `ops/` : observability and ops configuration