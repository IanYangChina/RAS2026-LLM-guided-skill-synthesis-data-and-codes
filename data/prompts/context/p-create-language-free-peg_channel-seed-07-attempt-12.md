## Search State

- **Seed**: 7
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → align → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.2088 | 0.42 | ❌ rejected |
| 11 | approach → align → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.3926 | 0.72 | ✅ accepted |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.2442 | 0.27 | ❌ rejected |
| 9 | approach → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.2975 | 0.56 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1961 | 0.12 | ❌ rejected |

**Proposal policy**: task_score is 0.42 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`
- Frozen object start: [0.5100076373283734, 0.11177710407756605, 0.04]
- Frozen task target: [0.5100076373283734, -0.04822289592243395, 0.04]
- Goal object position: (0.5100076373283734, -0.04822289592243395, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5100076373283734, 0.11177710407756605, 0.04)
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
  frozen_object_start: [0.51, 0.1118, 0.04]
  frozen_task_target: [0.51, -0.0482, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5100076373283734, 0.11177710407756605, 0.04]}
  frozen_targets: {'channel_exit': [0.5100076373283734, -0.04822289592243395, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.5100076373283734, 0.11177710407756605, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5100076373283734, -0.04822289592243395, 0.04) | final destination targets |
| `fixture` | offset from fixture pose (0.54, 0.0, 0.035) | approach/contact targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.209) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: align_standoff
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.05
  weight: 0.3
- id: push_goal
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.05
    tolerance: 0.005
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: align_standoff
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
    - 0.02
    - 0.0
    tolerance: 0.005
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: generator.speed
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
    - 0.0
    - 0.0
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: align_standoff
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.14
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: push_goal
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.01
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.05], tolerance=0.005
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **align_1** (`align`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], tolerance=0.005
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=reduce_speed
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.209
- **task_score** (E): 0.418
- **fitness_score**: 0.449  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2208 |
| align_1 | 1.00 | 1.00 | 0.0560 |
| contact_1 | 1.00 | 1.00 | 0.0024 |
| push_1 | 0.00 | 1.00 | 0.0999 |
| retract_1 | 1.00 | 1.00 | 0.1115 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.121, 0.096) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.554 | 2.732 |
| align_1 | align | 1.00 / step_budget | (0.505, 0.121, 0.096)→(0.505, 0.125, 0.042) | (0.502, 0.098, 0.034)→(0.504, 0.089, 0.032) | 0.178→0.170 | 1.00 / 2.000 | 116.400 | 225.776 |
| contact_1 | contact | 1.00 / force_exceeded | (0.505, 0.125, 0.042)→(0.504, 0.123, 0.041) | (0.504, 0.089, 0.032)→(0.505, 0.085, 0.028) | 0.170→0.165 | 1.00 / 2.333 | 82.820 | 82.820 |
| push_1 | push | 0.00 / step_budget | (0.504, 0.123, 0.041)→(0.505, 0.023, 0.041) | (0.505, 0.085, 0.028)→(0.501, 0.007, 0.033) | 0.165→0.091 | 1.00 / 2.667 | 98.259 | 150.625 |
| retract_1 | retract | 1.00 / step_budget | (0.505, 0.023, 0.041)→(0.497, -0.075, 0.083) | (0.501, 0.007, 0.033)→(0.505, -0.003, 0.028) | 0.091→0.082 | 1.00 / 1.333 | 0.565 | 89.726 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.735
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.735
- phase_score: 0.447
- phase_breakdown.push_goal_score: 0.468
- phase_breakdown.align_standoff_score: 0.398

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.562
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.735
- **Median Q (composite search score)**: 0.318
- **K-run variance**: 0.0248
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.356


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `474e87cb3f7f98c9c8d99c8760356b7c026b70b97898f68d5a6c39ba94bca956`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a79e5fd8fc80d9ecadd30a274b12d8d7e7d0841df5ca68ae512c46dc86b114e6`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.04741,"average_solve_count":232.0,"average_success_count":232.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.02314,"approach_1.speed":0.07399,"contact_1.contact_force":6.91224,"contact_1.speed":0.00854,"push_1.push_distance":0.18981,"push_1.push_speed":0.01104,"retract_1.retract_speed":0.05766},"optimized_scores":{"best_composite_score":0.32223,"best_fitness_score":0.56223,"best_task_score":0.73451},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":706.0,"contact_point_centroid":[0.51128,0.11732,0.00814],"force_p95":188.89833,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":203.52902,"mean_force":92.44881,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50621,0.13542,0.05853]},{"body_a":"attachment","body_b":"peg","contact_count":505.0,"contact_point_centroid":[0.51446,0.12731,0.05218],"force_p95":192.52168,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":202.96928,"mean_force":128.52894,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50759,0.13634,0.05077]},{"body_a":"peg","body_b":"channel_base_body","contact_count":921.0,"contact_point_centroid":[0.50753,0.0902,0.00846],"force_p95":153.11053,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":165.43377,"mean_force":93.40573,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51232,0.11166,0.04787]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":431.0,"contact_point_centroid":[0.52504,0.11946,0.06],"force_p95":128.89912,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":165.15593,"mean_force":77.90307,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51422,0.12542,0.05113]},{"body_a":"attachment","body_b":"peg","contact_count":963.0,"contact_point_centroid":[0.51222,0.10061,0.0492],"force_p95":152.00618,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":164.91468,"mean_force":91.71838,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5122,0.111,0.04768]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52198,0.119,0.00617],"force_p95":142.23718,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":142.23718,"mean_force":142.23718,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51054,0.14003,0.0447]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51471,0.12967,0.04743],"force_p95":141.30419,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":141.30419,"mean_force":141.30419,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51054,0.14003,0.0447]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":397.0,"contact_point_centroid":[0.47434,0.0603,0.03464],"force_p95":50.91991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":61.58735,"mean_force":14.81686,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50864,0.08205,0.04245]},{"body_a":"attachment","body_b":"peg","contact_count":171.0,"contact_point_centroid":[0.50014,0.02718,0.04616],"force_p95":33.15448,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.15282,"mean_force":23.7614,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50674,0.03679,0.04522]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":175.0,"contact_point_centroid":[0.47441,0.0127,0.03697],"force_p95":27.80824,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.17289,"mean_force":19.66495,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5067,0.03648,0.0453]},{"body_a":"peg","body_b":"channel_base_body","contact_count":885.0,"contact_point_centroid":[0.50205,-0.0002,0.00849],"force_p95":19.88945,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.20232,"mean_force":3.26127,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50124,-0.01464,0.0618]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":141.0,"contact_point_centroid":[0.52514,0.11655,0.05164],"force_p95":8.83083,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.77604,"mean_force":5.74692,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51472,0.13557,0.05004]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52505,-0.03014,0.02429],"force_p95":9.20468,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.28292,"mean_force":3.28807,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50109,-0.0074,0.05835]},{"body_a":"peg","body_b":"channel_base_body","contact_count":758.0,"contact_point_centroid":[0.50361,0.11169,0.00937],"force_p95":0.61049,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55557,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50223,0.16625,0.19433]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49979,0.19937,0.29905]}],"total_contact_groups":15},"final_pose_error":0.00991,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50562,-0.00575,0.02417],"final_tcp_position":[0.49688,-0.07359,0.08312],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":203.52902,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":780.0,"n_steps_budget":1000.0,"object_pos_end":[0.50366,0.11177,0.03381],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.54079,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":774.0,"raw_peak_contact_force":2.06328,"subtask_id":"align_standoff","tcp_end":[0.50605,0.13451,0.09619],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06644,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":706.0,"n_steps_budget":1000.0,"object_pos_end":[0.50639,0.11614,0.02879],"object_pos_start":[0.50366,0.11177,0.03381],"object_to_goal_dist_end":0.19657,"object_to_goal_dist_start":0.19191,"object_z_max":0.03391,"peak_contact_force":202.79771,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1211.0,"raw_peak_contact_force":203.52902,"tcp_end":[0.51054,0.14003,0.0447],"tcp_start":[0.50605,0.13451,0.09619],"tcp_to_object_dist_end":0.029,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50637,0.11618,0.02881],"object_pos_start":[0.50639,0.11614,0.02879],"object_to_goal_dist_end":0.1966,"object_to_goal_dist_start":0.19657,"object_z_max":0.02879,"peak_contact_force":142.23718,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":142.23718,"subtask_id":"align_standoff","tcp_end":[0.51055,0.14008,0.04472],"tcp_start":[0.51054,0.14003,0.0447],"tcp_to_object_dist_end":0.02901,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49232,0.02422,0.04019],"object_pos_start":[0.50637,0.11618,0.02881],"object_to_goal_dist_end":0.1045,"object_to_goal_dist_start":0.1966,"object_z_max":0.04019,"peak_contact_force":28.18361,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2853.0,"raw_peak_contact_force":165.43377,"subtask_id":"push_goal","tcp_end":[0.5085,0.04944,0.04179],"tcp_start":[0.51055,0.14008,0.04472],"tcp_to_object_dist_end":0.03001,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":892.0,"n_steps_budget":1000.0,"object_pos_end":[0.50562,-0.00575,0.02417],"object_pos_start":[0.49232,0.02422,0.04019],"object_to_goal_dist_end":0.07613,"object_to_goal_dist_start":0.1045,"object_z_max":0.04055,"peak_contact_force":0.60595,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1240.0,"raw_peak_contact_force":43.15282,"tcp_end":[0.49688,-0.07359,0.08312],"tcp_start":[0.5085,0.04944,0.04179],"tcp_to_object_dist_end":0.0903,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.84884,"average_solve_count":258.0,"average_success_count":258.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.0122,"approach_1.speed":0.06389,"contact_1.contact_force":6.43782,"contact_1.speed":0.01595,"push_1.push_distance":0.17569,"push_1.push_speed":0.04949,"retract_1.retract_speed":0.07132},"optimized_scores":{"best_composite_score":-0.01388,"best_fitness_score":0.22612,"best_task_score":0.16587},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.51342,0.09914,0.00675],"force_p95":167.25459,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":177.86094,"mean_force":139.37531,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50422,0.10945,0.04841]},{"body_a":"attachment","body_b":"peg","contact_count":1000.0,"contact_point_centroid":[0.51393,0.10506,0.05004],"force_p95":166.10801,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":171.73292,"mean_force":139.48501,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50422,0.10945,0.04841]},{"body_a":"attachment","body_b":"peg","contact_count":725.0,"contact_point_centroid":[0.49992,0.13524,0.04951],"force_p95":153.39981,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":161.94526,"mean_force":108.96452,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4955,0.14523,0.04827]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49954,0.11903,0.00794],"force_p95":125.80754,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":150.64047,"mean_force":70.17698,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49228,0.14381,0.05631]},{"body_a":"peg","body_b":"channel_base_body","contact_count":830.0,"contact_point_centroid":[0.50438,0.06694,0.00943],"force_p95":87.97897,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":115.91396,"mean_force":14.78293,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50106,-0.00595,0.06698]},{"body_a":"attachment","body_b":"peg","contact_count":210.0,"contact_point_centroid":[0.51319,0.05707,0.05717],"force_p95":104.4068,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":115.07153,"mean_force":55.84778,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50683,0.0487,0.05623]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50111,0.13991,0.04474],"force_p95":98.39511,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":98.39511,"mean_force":98.39511,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4988,0.15019,0.04256]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52117,0.11828,0.00697],"force_p95":73.90045,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.90045,"mean_force":73.90045,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4988,0.15019,0.04256]},{"body_a":"peg","body_b":"world","contact_count":479.0,"contact_point_centroid":[0.50248,0.12854,-0.00022],"force_p95":43.03155,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.62025,"mean_force":21.68981,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49749,0.14684,0.04595]},{"body_a":"peg","body_b":"world","contact_count":32.0,"contact_point_centroid":[0.50557,0.12482,-0.00013],"force_p95":25.76532,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.38213,"mean_force":13.06706,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49929,0.15072,0.04354]},{"body_a":"peg","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.50553,0.12479,-0.00035],"force_p95":27.42238,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.42238,"mean_force":27.42238,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4988,0.15019,0.04256]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":286.0,"contact_point_centroid":[0.52527,0.11075,0.03612],"force_p95":18.43541,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.57821,"mean_force":6.24618,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50345,0.13257,0.04829]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":73.0,"contact_point_centroid":[0.52514,0.07446,0.05783],"force_p95":14.40542,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.45181,"mean_force":8.35947,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50641,0.04919,0.05581]},{"body_a":"peg","body_b":"channel_base_body","contact_count":751.0,"contact_point_centroid":[0.49617,0.11909,0.00942],"force_p95":0.62144,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.5512,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49081,0.16972,0.19461]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49951,0.19917,0.29811]}],"total_contact_groups":15},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50209,0.07313,0.03444],"final_tcp_position":[0.49683,-0.07304,0.08361],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":177.86094,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":776.0,"n_steps_budget":1000.0,"object_pos_end":[0.49606,0.11914,0.03387],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19928,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.57388,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":775.0,"raw_peak_contact_force":2.24822,"subtask_id":"align_standoff","tcp_end":[0.48363,0.14145,0.09707],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06816,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50553,0.12148,0.02992],"object_pos_start":[0.49606,0.11914,0.03387],"object_to_goal_dist_end":0.20181,"object_to_goal_dist_start":0.19928,"object_z_max":0.03403,"peak_contact_force":145.98518,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2204.0,"raw_peak_contact_force":161.94526,"tcp_end":[0.4988,0.15019,0.04256],"tcp_start":[0.48363,0.14145,0.09707],"tcp_to_object_dist_end":0.03207,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50552,0.1215,0.02993],"object_pos_start":[0.50553,0.12148,0.02992],"object_to_goal_dist_end":0.20183,"object_to_goal_dist_start":0.20181,"object_z_max":0.02992,"peak_contact_force":98.39511,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":98.39511,"subtask_id":"align_standoff","tcp_end":[0.49878,0.15022,0.04255],"tcp_start":[0.4988,0.15019,0.04256],"tcp_to_object_dist_end":0.03209,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50675,0.07621,0.03068],"object_pos_start":[0.50552,0.1215,0.02993],"object_to_goal_dist_end":0.15664,"object_to_goal_dist_start":0.20183,"object_z_max":0.03069,"peak_contact_force":158.01229,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2318.0,"raw_peak_contact_force":177.86094,"subtask_id":"push_goal","tcp_end":[0.50668,0.06694,0.05041],"tcp_start":[0.49878,0.15022,0.04255],"tcp_to_object_dist_end":0.0218,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":832.0,"n_steps_budget":1000.0,"object_pos_end":[0.50209,0.07313,0.03444],"object_pos_start":[0.50675,0.07621,0.03068],"object_to_goal_dist_end":0.15325,"object_to_goal_dist_start":0.15664,"object_z_max":0.04065,"peak_contact_force":0.54072,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1113.0,"raw_peak_contact_force":115.91396,"tcp_end":[0.49683,-0.07304,0.08361],"tcp_start":[0.50668,0.06694,0.05041],"tcp_to_object_dist_end":0.15432,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.99593,"average_solve_count":246.0,"average_success_count":246.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.03779,"approach_1.speed":0.06125,"contact_1.contact_force":7.781,"contact_1.speed":0.01046,"push_1.push_distance":0.19545,"push_1.push_speed":0.0339,"retract_1.retract_speed":0.05064},"optimized_scores":{"best_composite_score":0.31807,"best_fitness_score":0.55807,"best_task_score":0.35356},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":112.0,"contact_point_centroid":[0.52507,0.08539,0.05999],"force_p95":276.6418,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":311.85514,"mean_force":193.71377,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51233,0.08544,0.05466]},{"body_a":"peg","body_b":"channel_base_body","contact_count":381.0,"contact_point_centroid":[0.50854,0.06388,0.00916],"force_p95":106.55375,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":110.69945,"mean_force":32.70072,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5142,0.08554,0.06346]},{"body_a":"attachment","body_b":"peg","contact_count":154.0,"contact_point_centroid":[0.51739,0.07493,0.05591],"force_p95":108.14296,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":110.26086,"mean_force":79.66656,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51223,0.08529,0.05531]},{"body_a":"attachment","body_b":"peg","contact_count":353.0,"contact_point_centroid":[0.49671,-0.05485,0.04526],"force_p95":105.28197,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":110.11012,"mean_force":78.96887,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4957,-0.04442,0.04008]},{"body_a":"peg","body_b":"channel_base_body","contact_count":557.0,"contact_point_centroid":[0.49552,-0.10109,0.03748],"force_p95":104.68018,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":110.07176,"mean_force":50.20263,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49576,-0.05154,0.04823]},{"body_a":"attachment","body_b":"peg","contact_count":743.0,"contact_point_centroid":[0.50083,-0.02387,0.04269],"force_p95":95.26481,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":108.58134,"mean_force":29.16938,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49842,-0.01235,0.03032]},{"body_a":"peg","body_b":"channel_base_body","contact_count":307.0,"contact_point_centroid":[0.49809,-0.10127,0.04188],"force_p95":100.31318,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":107.38279,"mean_force":67.28462,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49867,-0.04274,0.0302]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":15.0,"contact_point_centroid":[0.47495,-0.06825,0.0298],"force_p95":11.89183,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.96967,"mean_force":5.46709,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49574,-0.05441,0.05457]},{"body_a":"peg","body_b":"channel_base_body","contact_count":336.0,"contact_point_centroid":[0.49735,-0.06018,0.00936],"force_p95":7.35718,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.83586,"mean_force":1.05005,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49605,-0.06667,0.06548]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52511,-0.09972,0.0244],"force_p95":10.40301,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.71516,"mean_force":3.70022,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49628,-0.0763,0.07962]},{"body_a":"peg","body_b":"channel_base_body","contact_count":922.0,"contact_point_centroid":[0.50423,-0.04509,0.00956],"force_p95":5.35626,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.6469,"mean_force":1.81882,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49856,0.00191,0.03056]},{"body_a":"peg","body_b":"channel_base_body","contact_count":58.0,"contact_point_centroid":[0.50125,0.01996,0.00864],"force_p95":2.04133,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.82786,"mean_force":0.81703,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50343,0.08114,0.03629]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52505,0.03878,0.02366],"force_p95":7.51118,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.51118,"mean_force":7.51118,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50215,0.07887,0.03503]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":123.0,"contact_point_centroid":[0.52504,-0.05337,0.02738],"force_p95":5.94114,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.09697,"mean_force":2.32567,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49865,0.0042,0.0309]},{"body_a":"peg","body_b":"channel_base_body","contact_count":934.0,"contact_point_centroid":[0.50583,0.06296,0.00937],"force_p95":0.55536,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56105,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5118,0.14168,0.19201]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49973,0.19841,0.29707]}],"total_contact_groups":17},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50678,-0.07508,0.02535],"final_tcp_position":[0.49635,-0.07717,0.08115],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":311.85514,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":962.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.06302,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14328,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54646,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":968.0,"raw_peak_contact_force":3.88411,"subtask_id":"align_standoff","tcp_end":[0.52474,0.08758,0.09422],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06786,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":386.0,"n_steps_budget":1000.0,"object_pos_end":[0.49873,0.03076,0.03812],"object_pos_start":[0.50595,0.06302,0.03381],"object_to_goal_dist_end":0.11078,"object_to_goal_dist_start":0.14328,"object_z_max":0.04082,"peak_contact_force":0.41634,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":652.0,"raw_peak_contact_force":311.85514,"tcp_end":[0.50571,0.08365,0.03869],"tcp_start":[0.52474,0.08758,0.09422],"tcp_to_object_dist_end":0.05336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":64.0,"n_steps_budget":1000.0,"object_pos_end":[0.50402,0.01645,0.02393],"object_pos_start":[0.49873,0.03076,0.03812],"object_to_goal_dist_end":0.09786,"object_to_goal_dist_start":0.11078,"object_z_max":0.03812,"peak_contact_force":7.82786,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":59.0,"raw_peak_contact_force":7.82786,"subtask_id":"align_standoff","tcp_end":[0.50213,0.07882,0.03501],"tcp_start":[0.50571,0.08365,0.03869],"tcp_to_object_dist_end":0.06338,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50463,-0.07909,0.02788],"object_pos_start":[0.50402,0.01645,0.02393],"object_to_goal_dist_end":0.01301,"object_to_goal_dist_start":0.09786,"object_z_max":0.02857,"peak_contact_force":108.58134,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2095.0,"raw_peak_contact_force":108.58134,"subtask_id":"push_goal","tcp_end":[0.49884,-0.04607,0.02984],"tcp_start":[0.50213,0.07882,0.03501],"tcp_to_object_dist_end":0.03358,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":691.0,"n_steps_budget":870.0,"object_pos_end":[0.50678,-0.07508,0.02535],"object_pos_start":[0.50463,-0.07909,0.02788],"object_to_goal_dist_end":0.01688,"object_to_goal_dist_start":0.01301,"object_z_max":0.03689,"peak_contact_force":0.54698,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1275.0,"raw_peak_contact_force":110.11012,"tcp_end":[0.49635,-0.07717,0.08115],"tcp_start":[0.49884,-0.04607,0.02984],"tcp_to_object_dist_end":0.0568,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```