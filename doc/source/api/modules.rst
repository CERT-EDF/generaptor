API Reference
=============

This section contains the complete API reference for Generaptor, organized by module.

Main Package
------------

.. automodule:: generaptor
    :members:
    :member-order: bysource
    :show-inheritance:

Main Application
----------------

.. automodule:: generaptor.main
    :members:
    :member-order: bysource
    :show-inheritance:

Concepts Package
----------------

The concepts package contains the core data structures and logic.

.. automodule:: generaptor.concept.cache
    :members:
    :member-order: bysource
    :exclude-members: Cache
    :show-inheritance:

    .. autoclass:: Cache
        :members:
        :exclude-members: directory

.. automodule:: generaptor.concept.collection
    :members:
    :member-order: bysource
    :exclude-members: Outcome, Collection
    :show-inheritance:

    .. autoclass:: Outcome
        :members:
        :exclude-members: SUCCESS, PARTIAL, FAILURE

    .. autoclass:: Collection
        :members:
        :exclude-members: filepath

.. automodule:: generaptor.concept.collector
    :members:
    :member-order: bysource
    :exclude-members: Collector, CollectorConfig
    :show-inheritance:

    .. autoclass:: Collector
        :members:
        :exclude-members: config

    .. autoclass:: CollectorConfig
        :members:
        :exclude-members: device, rule_set, certificate, distribution, memdump, dont_be_lazy, vss_analysis_age, use_auto_accessor

.. automodule:: generaptor.concept.config
    :members:
    :member-order: bysource
    :exclude-members: Config
    :show-inheritance:

    .. autoclass:: Config
        :members:
        :exclude-members: directory

.. automodule:: generaptor.concept.distribution
    :members:
    :member-order: bysource
    :exclude-members: Architecture, OperatingSystem, Distribution
    :show-inheritance:

    .. autoclass:: Architecture
        :members:
        :exclude-members: X86, AMD64, AMD64_MUSL, ARM64, X86_LEGACY, AMD64_LEGACY

    .. autoclass:: OperatingSystem
        :members:
        :exclude-members: WINDOWS, DARWIN, LINUX, ANDROID, IOS

    .. autoclass:: Distribution
        :members:
        :exclude-members: arch, opsystem

.. automodule:: generaptor.concept.profile_set
    :members:
    :member-order: bysource
    :exclude-members: Profile, ProfileSet
    :show-inheritance:

    .. autoclass:: Profile
        :members:
        :exclude-members: guid, name, targets

    .. autoclass:: ProfileSet
        :members:
        :exclude-members: by_name, by_guid

.. automodule:: generaptor.concept.rule_set
    :members:
    :member-order: bysource
    :exclude-members: Rule, RuleSet
    :show-inheritance:

    .. autoclass:: Rule
        :members:
        :exclude-members: guid, name, category, glob, accessor, comment

    .. autoclass:: RuleSet
        :members:
        :exclude-members: by_guid

.. automodule:: generaptor.concept.target_set
    :members:
    :member-order: bysource
    :exclude-members: Target, TargetSet
    :show-inheritance:

    .. autoclass:: Target
        :members:
        :exclude-members: guid, name, rules

    .. autoclass:: TargetSet
        :members:
        :exclude-members: by_name, by_guid

Commands Package
----------------

The commands package contains all CLI command implementations.

.. automodule:: generaptor.command
    :members:
    :member-order: bysource
    :show-inheritance:

.. automodule:: generaptor.command.extract
    :members:
    :member-order: bysource
    :show-inheritance:

.. automodule:: generaptor.command.generate
    :members:
    :member-order: bysource
    :show-inheritance:

.. automodule:: generaptor.command.generate.darwin
    :members:
    :member-order: bysource
    :show-inheritance:

.. automodule:: generaptor.command.generate.helper
    :members:
    :member-order: bysource
    :show-inheritance:

.. automodule:: generaptor.command.generate.linux
    :members:
    :member-order: bysource
    :show-inheritance:

.. automodule:: generaptor.command.generate.windows
    :members:
    :member-order: bysource
    :show-inheritance:

.. automodule:: generaptor.command.get_fingerprint
    :members:
    :member-order: bysource
    :show-inheritance:

.. automodule:: generaptor.command.get_metadata
    :members:
    :member-order: bysource
    :show-inheritance:

.. automodule:: generaptor.command.get_profiles
    :members:
    :member-order: bysource
    :show-inheritance:

.. automodule:: generaptor.command.get_rules
    :members:
    :member-order: bysource
    :show-inheritance:

.. automodule:: generaptor.command.get_secret
    :members:
    :member-order: bysource
    :show-inheritance:

.. automodule:: generaptor.command.get_targets
    :members:
    :member-order: bysource
    :show-inheritance:

.. automodule:: generaptor.command.new_profile
    :members:
    :member-order: bysource
    :show-inheritance:

.. automodule:: generaptor.command.new_rule
    :members:
    :member-order: bysource
    :show-inheritance:

.. automodule:: generaptor.command.new_target
    :members:
    :member-order: bysource
    :show-inheritance:

.. automodule:: generaptor.command.update
    :members:
    :member-order: bysource
    :show-inheritance:

Helpers Package
---------------

The helpers package contains utility functions and classes.

.. automodule:: generaptor.helper
    :members:
    :member-order: bysource
    :show-inheritance:

.. automodule:: generaptor.helper.crypto
    :members:
    :member-order: bysource
    :show-inheritance:

.. automodule:: generaptor.helper.github
    :members:
    :member-order: bysource
    :exclude-members: GithubAsset, GithubRelease
    :show-inheritance:

    .. autoclass:: GithubAsset
        :members:
        :exclude-members: name, size, url, created_at

    .. autoclass:: GithubRelease
        :members:
        :exclude-members: name, tag, assets

.. automodule:: generaptor.helper.http
    :members:
    :member-order: bysource
    :show-inheritance:

.. automodule:: generaptor.helper.json
    :members:
    :member-order: bysource
    :show-inheritance:

.. automodule:: generaptor.helper.logging
    :members:
    :member-order: bysource
    :show-inheritance:

.. automodule:: generaptor.helper.prompt
    :members:
    :member-order: bysource
    :exclude-members: Option
    :show-inheritance:

    .. autoclass:: Option
        :members:
        :exclude-members: label, value

.. automodule:: generaptor.helper.validation
    :members:
    :member-order: bysource
    :show-inheritance:
