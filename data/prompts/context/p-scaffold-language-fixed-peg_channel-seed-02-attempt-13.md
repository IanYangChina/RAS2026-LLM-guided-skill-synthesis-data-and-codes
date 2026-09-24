## Search State

- **Seed**: 2
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | align → approach → descend → contact → push → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 13 | -0.1970 | 0.41 | ✅ accepted |
| 12 | approach → descend → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.0063 | 0.30 | ❌ rejected |
| 11 | approach → descend → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.1405 | 0.11 | ❌ rejected |
| 10 | approach → descend → align → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.2463 | 0.22 | ❌ rejected |
| 9 | approach → descend → align → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | -0.2805 | 0.30 | ❌ rejected |

**Proposal policy**: task_score is 0.41 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: peg_channel
- Frozen realised-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`
- Frozen object start: [0.48092897073994534, 0.06387929147312987, 0.04]
- Frozen task target: [0.48092897073994534, -0.09612070852687013, 0.04]
- Goal object position: (0.48092897073994534, -0.09612070852687013, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48092897073994534, 0.06387929147312987, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.2, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0.2, 0.3]
objects:
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    radius_m: 0.018
    half_length_m: 0.025
  - name: channel_structure
    role: fixture
    dynamics: static
    geometry: two_parallel_walls
    inner_gap_m: 0.05
    wall_thickness_m: 0.03
    wall_height_m: 0.05
task_landmarks:
  frozen_object_start: [0.4809, 0.0639, 0.04]
  frozen_task_target: [0.4809, -0.0961, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48092897073994534, 0.06387929147312987, 0.04]}
  frozen_targets: {'channel_exit': [0.48092897073994534, -0.09612070852687013, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.04, 0.00) | distance | — |
| contact | object | (0.00, 0.02, 0.00) | distance | — |
| push | world | (0.50, -0.08, 0.04) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=-0.197) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.04
    - 0.12
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.18
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    generator.speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.04
    - 0.005
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_z:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.005
      binds_to:
      - path: target.offset.z
        mode: replace
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.005
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 1.0
      - 8.0
      default: 3.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_offset_y:
      type: scalar
      range:
      - -0.005
      - 0.015
      default: 0.005
      binds_to:
      - path: target.offset.y
        mode: replace
    generator.speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_force_check
    when: after_phase
    predicate: force_below
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.002
    - 0.0
  subtask_id: contact
- id: lateral_align
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    generator.speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    lateral_push_x:
      type: scalar
      range:
      - -0.04
      - 0.04
      default: 0.02
      binds_to:
      - path: target.offset.x
        mode: add
  guards:
  - id: lateral_force_limit
    when: during_phase
    predicate: force_below
    threshold: 50.0
    on_failure: continue
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.12
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    generator.speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    push_depth:
      type: scalar
      range:
      - 0.05
      - 0.18
      default: 0.12
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: push_force_limit
    when: during_phase
    predicate: force_below
    threshold: 50.0
    on_failure: continue
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_1** (`align`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.12], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - generator.speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.005], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_z: status=consumed; consumers=target.offset.z (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.005, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_offset_y: status=consumed; consumers=target.offset.y (replace)
    - generator.speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_force_check, when=after_phase, predicate=force_below, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.002, 0.0]
- **lateral_align** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - generator.speed: status=consumed; consumers=generator.speed (replace)
    - lateral_push_x: status=consumed; consumers=target.offset.x (add)
  - guards:
    - id=lateral_force_limit, when=during_phase, predicate=force_below, on_failure=continue, threshold=50.0
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.12, mode=add_to_offset, sign=positive}, tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - generator.speed: status=consumed; consumers=generator.speed (replace)
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=push_force_limit, when=during_phase, predicate=force_below, on_failure=continue, threshold=50.0
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: -0.197
- **task_score** (E): 0.407
- **fitness_score**: 0.460  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.143
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.800

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2724 |
| approach_1 | 1.00 | 1.00 | 0.0789 |
| descend_1 | 1.00 | 1.00 | 0.0886 |
| contact_1 | 1.00 | 1.00 | 0.0076 |
| lateral_align | 0.33 | 1.00 | 0.0251 |
| push_1 | 0.33 | 1.00 | 0.1169 |
| retract_1 | 1.00 | 1.00 | 0.1181 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.496, 0.077, 0.059) | (0.494, 0.068, 0.040)→(0.499, 0.067, 0.033) | 0.151→0.148 | 1.00 / 2.333 | 338.990 | 483.278 |
| approach_1 | approach | 1.00 / step_budget | (0.496, 0.077, 0.059)→(0.496, 0.106, 0.130) | (0.499, 0.067, 0.033)→(0.499, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.000 | 0.545 | 61.484 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.106, 0.130)→(0.495, 0.107, 0.041) | (0.499, 0.068, 0.034)→(0.499, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.000 | 0.544 | 0.553 |
| contact_1 | contact | 1.00 / force_exceeded | (0.493, 0.089, 0.034)→(0.494, 0.082, 0.032) | (0.499, 0.068, 0.034)→(0.499, 0.067, 0.034) | 0.148→0.147 | 1.00 / 2.000 | 7.630 | 8.255 |
| lateral_align | push | 0.33 / guard_failure | (0.494, 0.082, 0.032)→(0.506, 0.061, 0.030) | (0.506, 0.054, 0.036)→(0.507, 0.031, 0.035) | 0.135→0.112 | 1.00 / 3.000 | 17.930 | 39.444 |
| push_1 | push | 0.33 / guard_failure | (0.506, 0.061, 0.030)→(0.504, -0.056, 0.029) | (0.507, 0.031, 0.035)→(0.499, -0.084, 0.037) | 0.112→0.006 | 1.00 / 2.333 | 56.937 | 56.937 |
| retract_1 | retract | 1.00 / step_budget | (0.504, -0.056, 0.029)→(0.501, -0.049, 0.147) | (0.499, -0.084, 0.037)→(0.498, -0.081, 0.034) | 0.006→0.009 | 1.00 / 1.333 | 0.375 | 44.465 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.897
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.631
- phase_score: 0.521
- phase_breakdown.approach_score: 0.141
- phase_breakdown.push_score: 0.595
- phase_breakdown.contact_score: 0.678

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.565
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.631
- **Median Q (composite search score)**: -0.246
- **K-run variance**: 0.0055
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.257


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `6269840a353345700ffa70ea476a3ad730b138bf2ec3c52304c054f0e194e023`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a2936262b79fcd5a49fda15d77b54223f43c58bfee2e71dc505f8a2f79369706`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09772,"average_solve_count":307.0,"average_success_count":307.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00418,"align_1.lateral_offset_y":-0.01579,"approach_1.approach_height":0.12486,"approach_1.generator.speed":0.15812,"contact_1.contact_force_threshold":5.61225,"contact_1.contact_offset_y":0.00564,"contact_1.generator.speed":0.03964,"descend_1.descend_z":-0.00128,"lateral_align.generator.speed":0.02524,"lateral_align.lateral_push_x":0.01101,"push_1.generator.speed":0.02125,"push_1.push_depth":0.1129,"retract_1.retract_height":0.14126},"optimized_scores":{"best_composite_score":-0.09242,"best_fitness_score":0.56472,"best_task_score":0.63058},"replay_outcomes":[{"contacts":{"omitted_contact_groups":6,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":64.0,"contact_point_centroid":[0.47498,0.05452,0.05984],"force_p95":418.60677,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":444.23331,"mean_force":381.85295,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48517,0.06043,0.05845]},{"body_a":"peg","body_b":"channel_base_body","contact_count":941.0,"contact_point_centroid":[0.496,0.06327,0.00936],"force_p95":36.56427,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":155.2363,"mean_force":5.99257,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48996,0.122,0.16346]},{"body_a":"attachment","body_b":"peg","contact_count":92.0,"contact_point_centroid":[0.49741,0.05953,0.05757],"force_p95":135.71617,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":155.17856,"mean_force":55.70367,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48553,0.06026,0.05824]},{"body_a":"peg","body_b":"channel_base_body","contact_count":279.0,"contact_point_centroid":[0.49597,0.06568,0.00939],"force_p95":21.79134,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":66.15237,"mean_force":2.81364,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48933,0.08343,0.09322]},{"body_a":"attachment","body_b":"peg","contact_count":41.0,"contact_point_centroid":[0.49791,0.05585,0.05849],"force_p95":45.01867,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.41014,"mean_force":15.52261,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48781,0.0613,0.05867]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52508,0.04779,0.05999],"force_p95":51.42841,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":52.72347,"mean_force":39.13812,"phase_index":4.0,"phase_name":"lateral_align","phase_type":"push","tcp_position_centroid":[0.50787,0.04792,0.0303]},{"body_a":"attachment","body_b":"peg","contact_count":144.0,"contact_point_centroid":[0.50632,-0.0084,0.03629],"force_p95":7.69093,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.75076,"mean_force":2.28866,"phase_index":5.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50518,0.00337,0.02822]},{"body_a":"peg","body_b":"channel_base_body","contact_count":14.0,"contact_point_centroid":[0.50033,-0.10105,0.03854],"force_p95":30.36654,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.81082,"mean_force":8.00191,"phase_index":5.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50414,-0.0527,0.02879]},{"body_a":"attachment","body_b":"peg","contact_count":19.0,"contact_point_centroid":[0.50189,-0.06842,0.03943],"force_p95":35.7477,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.35841,"mean_force":16.02483,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50281,-0.05718,0.03056]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.5251,0.04752,0.05998],"force_p95":38.25079,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":40.04483,"mean_force":26.22748,"phase_index":5.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50787,0.04765,0.03015]},{"body_a":"peg","body_b":"channel_base_body","contact_count":40.0,"contact_point_centroid":[0.49753,-0.10154,0.04296],"force_p95":33.16881,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.61384,"mean_force":7.83206,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50214,-0.05522,0.03529]},{"body_a":"attachment","body_b":"peg","contact_count":196.0,"contact_point_centroid":[0.5037,0.04822,0.04478],"force_p95":21.08896,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.43774,"mean_force":6.66587,"phase_index":4.0,"phase_name":"lateral_align","phase_type":"push","tcp_position_centroid":[0.49864,0.05981,0.02894]},{"body_a":"peg","body_b":"channel_base_body","contact_count":95.0,"contact_point_centroid":[0.50338,-0.02491,0.00978],"force_p95":5.5356,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.86163,"mean_force":2.538,"phase_index":5.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50556,0.01039,0.0285]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":54.0,"contact_point_centroid":[0.52519,-0.03848,0.03063],"force_p95":9.38877,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.09279,"mean_force":1.5605,"phase_index":5.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50508,-0.00842,0.02843]},{"body_a":"peg","body_b":"channel_base_body","contact_count":181.0,"contact_point_centroid":[0.49725,-0.07915,0.00957],"force_p95":0.74374,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.76214,"mean_force":0.63116,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5014,-0.0467,0.09249]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":235.0,"contact_point_centroid":[0.5252,0.02959,0.03462],"force_p95":14.70807,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.62778,"mean_force":3.65383,"phase_index":4.0,"phase_name":"lateral_align","phase_type":"push","tcp_position_centroid":[0.49953,0.0585,0.02893]}],"total_contact_groups":22},"final_pose_error":0.02996,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49299,-0.07971,0.03382],"final_tcp_position":[0.50163,-0.05039,0.14102],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":444.23331,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":968.0,"n_steps_budget":1000.0,"object_pos_end":[0.49693,0.06222,0.03179],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14249,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":132.91649,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1125.0,"raw_peak_contact_force":444.23331,"tcp_end":[0.48814,0.05785,0.05468],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0249,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":279.0,"n_steps_budget":600.0,"object_pos_end":[0.4963,0.06313,0.03402],"object_pos_start":[0.49693,0.06222,0.03179],"object_to_goal_dist_end":0.1433,"object_to_goal_dist_start":0.14249,"object_z_max":0.03664,"peak_contact_force":0.54346,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":320.0,"raw_peak_contact_force":66.15237,"subtask_id":"approach","tcp_end":[0.49286,0.09974,0.13724],"tcp_start":[0.48814,0.05785,0.05468],"tcp_to_object_dist_end":0.10958,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":311.0,"n_steps_budget":660.0,"object_pos_end":[0.49613,0.06302,0.034],"object_pos_start":[0.4963,0.06313,0.03402],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.1433,"object_z_max":0.03402,"peak_contact_force":0.54143,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":311.0,"raw_peak_contact_force":0.5541,"tcp_end":[0.49221,0.10195,0.04164],"tcp_start":[0.49286,0.09974,0.13724],"tcp_to_object_dist_end":0.03987,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":575.0,"n_steps_budget":600.0,"object_pos_end":[0.49654,0.06198,0.03493],"object_pos_start":[0.49613,0.06302,0.034],"object_to_goal_dist_end":0.14212,"object_to_goal_dist_start":0.1432,"object_z_max":0.03606,"peak_contact_force":0.13941,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":946.0,"raw_peak_contact_force":9.11627,"subtask_id":"contact","tcp_end":[0.49204,0.07118,0.0304],"tcp_start":[0.48976,0.09118,0.03496],"tcp_to_object_dist_end":0.01119,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":274.0,"n_steps_budget":930.0,"object_pos_end":[0.50713,0.01771,0.0349],"object_pos_start":[0.50486,0.04355,0.03608],"object_to_goal_dist_end":0.0981,"object_to_goal_dist_start":0.12371,"object_z_max":0.03621,"peak_contact_force":52.72347,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":627.0,"raw_peak_contact_force":52.72347,"tcp_end":[0.50799,0.04779,0.03032],"tcp_start":[0.49204,0.07118,0.0304],"tcp_to_object_dist_end":0.03044,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":199.0,"n_steps_budget":1000.0,"object_pos_end":[0.49998,-0.08564,0.03782],"object_pos_start":[0.50713,0.01771,0.0349],"object_to_goal_dist_end":0.00605,"object_to_goal_dist_start":0.0981,"object_z_max":0.03987,"peak_contact_force":50.75076,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":316.0,"raw_peak_contact_force":50.75076,"tcp_end":[0.50411,-0.0569,0.0289],"tcp_start":[0.50799,0.04779,0.03032],"tcp_to_object_dist_end":0.03037,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":220.0,"n_steps_budget":900.0,"object_pos_end":[0.49299,-0.07971,0.03382],"object_pos_start":[0.49998,-0.08564,0.03782],"object_to_goal_dist_end":0.00935,"object_to_goal_dist_start":0.00605,"object_z_max":0.0391,"peak_contact_force":0.5501,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":390.0,"raw_peak_contact_force":40.35841,"tcp_end":[0.50163,-0.05039,0.14102],"tcp_start":[0.50411,-0.0569,0.0289],"tcp_to_object_dist_end":0.11147,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `78f29ebb38dd2df9149fb0cd7c7c33d55e802bb94eee599b284bb0b197a04fb7`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31273,"average_solve_count":275.0,"average_success_count":275.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00162,"align_1.lateral_offset_y":-0.00411,"approach_1.approach_height":0.11621,"approach_1.generator.speed":0.17705,"contact_1.contact_force_threshold":3.35407,"contact_1.contact_offset_y":0.00492,"contact_1.generator.speed":0.04591,"descend_1.descend_z":-0.00425,"lateral_align.generator.speed":0.02934,"lateral_align.lateral_push_x":0.01716,"push_1.generator.speed":0.03091,"push_1.push_depth":0.10338,"retract_1.retract_height":0.12876},"optimized_scores":{"best_composite_score":-0.24555,"best_fitness_score":0.41159,"best_task_score":0.29308},"replay_outcomes":[{"contacts":{"omitted_contact_groups":10,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":91.0,"contact_point_centroid":[0.47498,0.05681,0.05985],"force_p95":478.29771,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":494.84591,"mean_force":460.29029,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46974,0.06751,0.06044]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52509,0.04844,0.05998],"force_p95":51.04262,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":52.67875,"mean_force":36.18993,"phase_index":4.0,"phase_name":"lateral_align","phase_type":"push","tcp_position_centroid":[0.5075,0.04858,0.0283]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.49675,-0.10058,0.04907],"force_p95":47.00167,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.28564,"mean_force":35.52844,"phase_index":5.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50407,-0.05453,0.02871]},{"body_a":"attachment","body_b":"peg","contact_count":160.0,"contact_point_centroid":[0.50483,-0.01038,0.03625],"force_p95":3.64817,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.04414,"mean_force":1.99469,"phase_index":5.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50492,0.00124,0.0271]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.475,0.05601,0.05998],"force_p95":46.65655,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":47.33003,"mean_force":34.34158,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47113,0.06732,0.06052]},{"body_a":"peg","body_b":"channel_base_body","contact_count":101.0,"contact_point_centroid":[0.49412,-0.10068,0.03632],"force_p95":1.97365,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.36748,"mean_force":0.91806,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50179,-0.05028,0.05869]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50038,-0.06723,0.02938],"force_p95":43.05645,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.05645,"mean_force":43.05645,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50407,-0.05583,0.02876]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52512,0.04818,0.05998],"force_p95":25.85545,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":26.55991,"mean_force":14.59998,"phase_index":5.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50753,0.04832,0.02815]},{"body_a":"attachment","body_b":"peg","contact_count":170.0,"contact_point_centroid":[0.50344,0.04554,0.04285],"force_p95":10.37069,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.45787,"mean_force":3.64882,"phase_index":4.0,"phase_name":"lateral_align","phase_type":"push","tcp_position_centroid":[0.49806,0.05711,0.02696]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.47497,-0.08192,0.01384],"force_p95":11.14563,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.15894,"mean_force":11.02585,"phase_index":5.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50408,-0.054,0.0287]},{"body_a":"peg","body_b":"channel_base_body","contact_count":921.0,"contact_point_centroid":[0.49474,0.05962,0.0094],"force_p95":7.11647,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.78906,"mean_force":1.21456,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48144,0.12533,0.16341]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":230.0,"contact_point_centroid":[0.52522,0.0271,0.03251],"force_p95":7.87317,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.75465,"mean_force":1.93322,"phase_index":4.0,"phase_name":"lateral_align","phase_type":"push","tcp_position_centroid":[0.49919,0.05598,0.027]},{"body_a":"peg","body_b":"channel_base_body","contact_count":169.0,"contact_point_centroid":[0.50673,0.0121,0.00997],"force_p95":7.46726,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.41363,"mean_force":2.99112,"phase_index":4.0,"phase_name":"lateral_align","phase_type":"push","tcp_position_centroid":[0.49901,0.05625,0.0271]},{"body_a":"attachment","body_b":"peg","contact_count":90.0,"contact_point_centroid":[0.48161,0.06635,0.05923],"force_p95":9.13199,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.35708,"mean_force":6.7747,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46976,0.06751,0.06043]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":21.0,"contact_point_centroid":[0.4748,-0.08365,0.04886],"force_p95":6.38464,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.11069,"mean_force":1.17194,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50197,-0.05271,0.04086]},{"body_a":"peg","body_b":"channel_base_body","contact_count":92.0,"contact_point_centroid":[0.5025,-0.02825,0.00984],"force_p95":5.12962,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.41683,"mean_force":2.23196,"phase_index":5.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50523,0.00615,0.02726]}],"total_contact_groups":26},"final_pose_error":0.02953,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49386,-0.08198,0.03378],"final_tcp_position":[0.50154,-0.04976,0.12874],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":494.84591,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":950.0,"n_steps_budget":1000.0,"object_pos_end":[0.49555,0.05898,0.03457],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13916,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":474.27456,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1137.0,"raw_peak_contact_force":494.84591,"tcp_end":[0.47113,0.06731,0.06051],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03659,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":248.0,"n_steps_budget":600.0,"object_pos_end":[0.49569,0.05901,0.03381],"object_pos_start":[0.49555,0.05898,0.03457],"object_to_goal_dist_end":0.13921,"object_to_goal_dist_start":0.13916,"object_z_max":0.03457,"peak_contact_force":0.54609,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":258.0,"raw_peak_contact_force":47.33003,"subtask_id":"approach","tcp_end":[0.4889,0.09756,0.13201],"tcp_start":[0.47113,0.06731,0.06051],"tcp_to_object_dist_end":0.10571,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":308.0,"n_steps_budget":660.0,"object_pos_end":[0.49549,0.05904,0.03389],"object_pos_start":[0.49569,0.05901,0.03381],"object_to_goal_dist_end":0.13924,"object_to_goal_dist_start":0.13921,"object_z_max":0.03389,"peak_contact_force":0.54298,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":308.0,"raw_peak_contact_force":0.55415,"tcp_end":[0.49114,0.09811,0.03842],"tcp_start":[0.4889,0.09756,0.13201],"tcp_to_object_dist_end":0.03957,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":595.0,"n_steps_budget":600.0,"object_pos_end":[0.49572,0.05875,0.03397],"object_pos_start":[0.49549,0.05904,0.03389],"object_to_goal_dist_end":0.13895,"object_to_goal_dist_start":0.13924,"object_z_max":0.03615,"peak_contact_force":12.53687,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":966.0,"raw_peak_contact_force":5.43401,"subtask_id":"contact","tcp_end":[0.4906,0.06581,0.02807],"tcp_start":[0.49119,0.06737,0.02937],"tcp_to_object_dist_end":0.01053,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":242.0,"n_steps_budget":930.0,"object_pos_end":[0.50712,0.01848,0.03491],"object_pos_start":[0.50621,0.03926,0.03598],"object_to_goal_dist_end":0.09887,"object_to_goal_dist_start":0.11949,"object_z_max":0.0365,"peak_contact_force":0.0,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":577.0,"raw_peak_contact_force":52.67875,"tcp_end":[0.50765,0.04848,0.02833],"tcp_start":[0.4906,0.06581,0.02807],"tcp_to_object_dist_end":0.03071,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":193.0,"n_steps_budget":1000.0,"object_pos_end":[0.49543,-0.08425,0.03666],"object_pos_start":[0.50712,0.01848,0.03491],"object_to_goal_dist_end":0.00708,"object_to_goal_dist_start":0.09887,"object_z_max":0.03735,"peak_contact_force":49.28564,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":272.0,"raw_peak_contact_force":49.28564,"tcp_end":[0.50407,-0.05583,0.02876],"tcp_start":[0.50765,0.04848,0.02833],"tcp_to_object_dist_end":0.03074,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":196.0,"n_steps_budget":810.0,"object_pos_end":[0.49386,-0.08198,0.03378],"object_pos_start":[0.49543,-0.08425,0.03666],"object_to_goal_dist_end":0.00896,"object_to_goal_dist_start":0.00708,"object_z_max":0.03684,"peak_contact_force":0.02519,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":297.0,"raw_peak_contact_force":44.36748,"tcp_end":[0.50154,-0.04976,0.12874],"tcp_start":[0.50407,-0.05583,0.02876],"tcp_to_object_dist_end":0.10057,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ecba62e37d233197bb248f7fe6e722b45204af5e83240a6f27138a89bcccfe42`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23793,"average_solve_count":290.0,"average_success_count":290.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00185,"align_1.lateral_offset_y":0.01507,"approach_1.approach_height":0.10636,"approach_1.generator.speed":0.16824,"contact_1.contact_force_threshold":3.68561,"contact_1.contact_offset_y":-0.00213,"contact_1.generator.speed":0.04206,"descend_1.descend_z":0.00117,"lateral_align.generator.speed":0.02474,"lateral_align.lateral_push_x":0.00099,"push_1.generator.speed":0.02437,"push_1.push_depth":0.14764,"retract_1.retract_height":0.17058},"optimized_scores":{"best_composite_score":-0.25299,"best_fitness_score":0.40415,"best_task_score":0.29796},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":94.0,"contact_point_centroid":[0.53942,0.10496,0.05982],"force_p95":481.13393,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":510.75383,"mean_force":411.86479,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52756,0.10539,0.06138]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.54046,0.10511,0.05995],"force_p95":70.16488,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":70.96991,"mean_force":54.76999,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52861,0.10531,0.06179]},{"body_a":"peg","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.502,-0.10032,0.05471],"force_p95":63.58497,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":70.77469,"mean_force":45.12402,"phase_index":5.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50251,-0.05244,0.02952]},{"body_a":"attachment","body_b":"peg","contact_count":178.0,"contact_point_centroid":[0.50429,0.00983,0.04095],"force_p95":33.0969,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.2545,"mean_force":5.45761,"phase_index":5.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50066,0.02133,0.02863]},{"body_a":"peg","body_b":"channel_base_body","contact_count":84.0,"contact_point_centroid":[0.50418,-0.10058,0.03911],"force_p95":0.99893,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.67058,"mean_force":1.10173,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50019,-0.04711,0.0599]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.50259,-0.06669,0.03387],"force_p95":34.24778,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.8879,"mean_force":6.81432,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50195,-0.05504,0.02978]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":114.0,"contact_point_centroid":[0.52523,0.00624,0.03038],"force_p95":27.59591,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.5091,"mean_force":3.3471,"phase_index":5.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50038,0.03592,0.0286]},{"body_a":"peg","body_b":"channel_base_body","contact_count":98.0,"contact_point_centroid":[0.50471,-0.02425,0.00974],"force_p95":15.19575,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.66699,"mean_force":3.9813,"phase_index":5.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50084,0.01647,0.02874]},{"body_a":"peg","body_b":"channel_base_body","contact_count":88.0,"contact_point_centroid":[0.50726,0.05278,0.00994],"force_p95":11.23016,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.93084,"mean_force":7.78622,"phase_index":4.0,"phase_name":"lateral_align","phase_type":"push","tcp_position_centroid":[0.49927,0.09903,0.03284]},{"body_a":"attachment","body_b":"peg","contact_count":123.0,"contact_point_centroid":[0.5039,0.08645,0.04414],"force_p95":11.66336,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.39895,"mean_force":5.61842,"phase_index":4.0,"phase_name":"lateral_align","phase_type":"push","tcp_position_centroid":[0.49934,0.0981,0.03258]},{"body_a":"peg","body_b":"channel_base_body","contact_count":124.0,"contact_point_centroid":[0.50633,0.07849,0.0094],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.21412,"mean_force":0.86738,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50019,0.11433,0.03951]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.50397,0.0981,0.05343],"force_p95":9.96006,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.99086,"mean_force":7.07981,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49935,0.10988,0.037]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":100.0,"contact_point_centroid":[0.52514,0.06858,0.03114],"force_p95":5.87587,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.75486,"mean_force":2.20808,"phase_index":4.0,"phase_name":"lateral_align","phase_type":"push","tcp_position_centroid":[0.49927,0.09746,0.03226]},{"body_a":"peg","body_b":"channel_base_body","contact_count":880.0,"contact_point_centroid":[0.50581,0.08086,0.00937],"force_p95":0.55092,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.56411,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51433,0.14627,0.16319]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49992,0.19826,0.29578]},{"body_a":"peg","body_b":"channel_base_body","contact_count":264.0,"contact_point_centroid":[0.50347,-0.07925,0.00955],"force_p95":0.75946,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.69488,"mean_force":0.57372,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49991,-0.04302,0.10086]}],"total_contact_groups":19},"final_pose_error":0.0298,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50623,-0.08187,0.03379],"final_tcp_position":[0.50021,-0.04744,0.17115],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":510.75383,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":909.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":409.77874,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1010.0,"raw_peak_contact_force":510.75383,"tcp_end":[0.52856,0.1053,0.06178],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04349,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":195.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.54458,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":198.0,"raw_peak_contact_force":70.96991,"subtask_id":"approach","tcp_end":[0.50727,0.12104,0.12049],"tcp_start":[0.52856,0.1053,0.06178],"tcp_to_object_dist_end":0.09558,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":243.0,"n_steps_budget":600.0,"object_pos_end":[0.50595,0.08088,0.03378],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.16111,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":0.5464,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":243.0,"raw_peak_contact_force":0.55006,"tcp_end":[0.50247,0.12002,0.04421],"tcp_start":[0.50727,0.12104,0.12049],"tcp_to_object_dist_end":0.04065,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":124.0,"n_steps_budget":660.0,"object_pos_end":[0.50598,0.08071,0.03396],"object_pos_start":[0.50595,0.08088,0.03378],"object_to_goal_dist_end":0.16094,"object_to_goal_dist_start":0.16111,"object_z_max":0.03485,"peak_contact_force":10.21412,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":130.0,"raw_peak_contact_force":10.21412,"subtask_id":"contact","tcp_end":[0.499,0.10911,0.0363],"tcp_start":[0.49905,0.10919,0.03639],"tcp_to_object_dist_end":0.02934,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":143.0,"n_steps_budget":780.0,"object_pos_end":[0.50703,0.05768,0.03533],"object_pos_start":[0.50603,0.08012,0.03489],"object_to_goal_dist_end":0.13793,"object_to_goal_dist_start":0.16031,"object_z_max":0.03579,"peak_contact_force":1.06634,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":311.0,"raw_peak_contact_force":12.93084,"tcp_end":[0.50127,0.08716,0.03077],"tcp_start":[0.499,0.10911,0.0363],"tcp_to_object_dist_end":0.03039,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":259.0,"n_steps_budget":1000.0,"object_pos_end":[0.50213,-0.08334,0.03777],"object_pos_start":[0.50703,0.05768,0.03533],"object_to_goal_dist_end":0.00455,"object_to_goal_dist_start":0.13793,"object_z_max":0.03843,"peak_contact_force":70.77469,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":397.0,"raw_peak_contact_force":70.77469,"tcp_end":[0.5025,-0.05442,0.02946],"tcp_start":[0.50127,0.08716,0.03077],"tcp_to_object_dist_end":0.0301,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":276.0,"n_steps_budget":1000.0,"object_pos_end":[0.50623,-0.08187,0.03379],"object_pos_start":[0.50213,-0.08334,0.03777],"object_to_goal_dist_end":0.00899,"object_to_goal_dist_start":0.00455,"object_z_max":0.03849,"peak_contact_force":0.5489,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":388.0,"raw_peak_contact_force":48.67058,"tcp_end":[0.50021,-0.04744,0.17115],"tcp_start":[0.5025,-0.05442,0.02946],"tcp_to_object_dist_end":0.14174,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```