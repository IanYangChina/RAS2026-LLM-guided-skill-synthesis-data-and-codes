## Search State

- **Seed**: 8
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | time_limit | 5  | 0.0851 | 0.15 | ✅ accepted |
| 0 | pull → insert → descend → contact → release | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | contact_detected | force_exceeded | time_limit | 5  | 0.1320 | 0.18 | ✅ accepted |

**Proposal policy**: task_score is 0.18 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: grasp_place
- Frozen realised-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`
- Frozen object start: [0.48269722766055606, 0.048727684333792556, 0.03]
- Frozen task target: [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]
- Goal object position: (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.48269722766055606, 0.048727684333792556, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.4827, 0.0487, 0.03]
  frozen_task_target: [0.5819, 0.2289, 0.2305]
  frozen_object_starts: {'grasp_target': [0.48269722766055606, 0.048727684333792556, 0.03]}
  frozen_targets: {'place_target': [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c

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
| `object` | offset from object initial position (0.48269722766055606, 0.048727684333792556, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5818710838485517, 0.2288548935820029, 0.2304844767544324) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

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

## Current Skill (Q=0.132) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_pregrasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.1
- id: reach_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.1
- id: lift_object
  target_entity: object
  metric: goal_progress
  weight: 0.3
- id: place_object
  target_entity: object
  weight: 0.5
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.12
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    pregrasp_height:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_pregrasp
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.03
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_grasp
- id: grasp_1
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.2
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: abort
  subtask_id: lift_object
- id: transport_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
    orientation:
      mode: keep_current
  parameters:
    transport_z_offset:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_object
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.04
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.2
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.12]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - pregrasp_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03]
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.2]
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=abort, threshold=0.05
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15]
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_z_offset: status=consumed; consumers=target.offset.z (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.2]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.132
- **task_score** (E): 0.182
- **fitness_score**: 0.562  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1360 |
| descend_1 | 1.00 | 1.00 | 0.1247 |
| grasp_1 | 1.00 | 1.00 | 0.0123 |
| lift_1 | 1.00 | 1.00 | 0.1120 |
| transport_1 | 0.00 | 1.00 | 0.0988 |
| descend_2 | 1.00 | 1.00 | 0.1099 |
| release_1 | 1.00 | 1.00 | 0.0216 |
| retract_1 | 1.00 | 1.00 | 0.1555 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.172) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.516, -0.001, 0.172)→(0.517, -0.001, 0.047) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.517, -0.001, 0.047)→(0.509, -0.001, 0.038) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 41.667 | 0.143 | 0.200 |
| lift_1 | lift | 1.00 / step_budget | (0.509, -0.001, 0.038)→(0.517, -0.001, 0.150) | (0.522, -0.001, 0.026)→(0.530, -0.001, 0.129) | 0.289→0.237 | 1.00 / 22.667 | 0.124 | 0.488 |
| transport_1 | approach | 0.00 / step_budget | (0.517, -0.001, 0.150)→(0.546, 0.073, 0.206) | (0.530, -0.001, 0.129)→(0.540, 0.049, 0.016) | 0.237→0.258 | 1.00 / 8.333 | 0.123 | 1.559 |
| descend_2 | descend | 1.00 / step_budget | (0.546, 0.073, 0.206)→(0.589, 0.172, 0.201) | (0.540, 0.049, 0.016)→(0.540, 0.049, 0.016) | 0.258→0.258 | 1.00 / 8.333 | 91002.368 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.589, 0.172, 0.201)→(0.584, 0.171, 0.222) | (0.540, 0.049, 0.016)→(0.540, 0.049, 0.016) | 0.258→0.258 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 1.00 / time_limit | (0.584, 0.171, 0.222)→(0.582, 0.170, 0.378) | (0.540, 0.049, 0.016)→(0.540, 0.049, 0.016) | 0.258→0.258 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.227
- phase_score: 0.236
- phase_breakdown.reach_grasp_score: 0.840
- phase_breakdown.place_object_score: 0.064
- phase_breakdown.lift_object_score: 0.169
- phase_breakdown.reach_pregrasp_score: 0.699
- grasp_place_fitness: 0.579

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.579
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.227
- **Median Q (composite search score)**: 0.132
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.328


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2cbd02033d1f1347f2ac2d0b012406a96501e6b48f5b172bd88b34d6c745630c`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5745d7c2d025a63f908a4bf0f58182445bb06541d436718f39304ac5569d60c0`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91124,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.pregrasp_height":0.12027,"descend_1.grasp_z_offset":0.00193,"descend_2.place_z_offset":0.00694,"lift_1.lift_height":0.11433,"transport_1.transport_z_offset":0.14077},"optimized_scores":{"best_composite_score":0.13223,"best_fitness_score":0.56223,"best_task_score":0.16452},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1994.0,"contact_point_centroid":[0.49065,0.09129,-0.00246],"force_p95":0.1927,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.5989,"mean_force":0.1479,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50172,0.09402,0.18661]},{"body_a":"world","body_b":"grasp_target","contact_count":139.0,"contact_point_centroid":[0.48071,0.04586,-0.00122],"force_p95":0.43263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60612,"mean_force":0.06697,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46943,0.04689,0.03068]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10013.0,"contact_point_centroid":[0.47406,0.02772,0.07715],"force_p95":0.10342,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30742,"mean_force":0.06482,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47213,0.04666,0.07513]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10724.0,"contact_point_centroid":[0.47382,0.06558,0.07404],"force_p95":0.10043,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30329,"mean_force":0.06151,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47185,0.04667,0.07242]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4330.0,"contact_point_centroid":[0.48801,0.0802,0.14323],"force_p95":0.15016,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29288,"mean_force":0.09736,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48354,0.06196,0.14476]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48276,0.04837,-0.00215],"force_p95":0.16848,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2486,"mean_force":0.13456,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47166,0.04716,0.0299]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4132.0,"contact_point_centroid":[0.48778,0.04266,0.14228],"force_p95":0.15854,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24195,"mean_force":0.09568,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48302,0.06092,0.14348]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3853.0,"contact_point_centroid":[0.47109,0.02778,0.03179],"force_p95":0.08598,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15554,"mean_force":0.05472,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47056,0.04705,0.02878]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.4827,0.04873,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48962,0.02148,0.22916]},{"body_a":"world","body_b":"grasp_target","contact_count":1568.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47823,0.04579,0.09714]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49056,0.09119,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.53653,0.15708,0.21205]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.49056,0.09119,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55702,0.19579,0.22345]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49056,0.09119,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55384,0.19443,0.3179]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5527.0,"contact_point_centroid":[0.46999,0.06617,0.03129],"force_p95":0.07078,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08151,"mean_force":0.04078,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47056,0.04705,0.02879]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1877.0,"contact_point_centroid":[0.50286,0.09566,0.19097],"force_p95":0.01151,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01647,"mean_force":0.01064,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50266,0.09564,0.18875]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4281.0,"contact_point_centroid":[0.53695,0.15729,0.21448],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01042,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.53664,0.15726,0.21209]}],"total_contact_groups":17},"final_pose_error":0.04271,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.49056,0.09119,0.01602],"final_tcp_position":[0.55471,0.19465,0.40076],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.5989,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":452.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1804.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pregrasp","tcp_end":[0.48075,0.04403,0.15865],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13273,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":392.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1568.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.47824,0.04781,0.03667],"tcp_start":[0.48075,0.04403,0.15865],"tcp_to_object_dist_end":0.01158,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48262,0.04706,0.02549],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29141,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15802,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11180.0,"raw_peak_contact_force":0.2486,"tcp_end":[0.47053,0.04704,0.02875],"tcp_start":[0.47824,0.04781,0.03667],"tcp_to_object_dist_end":0.01253,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.49496,0.04684,0.11751],"object_pos_start":[0.48262,0.04706,0.02549],"object_to_goal_dist_end":0.23118,"object_to_goal_dist_start":0.29141,"object_z_max":0.11741,"peak_contact_force":0.10188,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20876.0,"raw_peak_contact_force":0.60612,"subtask_id":"lift_object","tcp_end":[0.478,0.04669,0.12836],"tcp_start":[0.47053,0.04704,0.02875],"tcp_to_object_dist_end":0.02013,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49056,0.09119,0.01602],"object_pos_start":[0.49496,0.04684,0.11751],"object_to_goal_dist_end":0.27071,"object_to_goal_dist_start":0.23118,"object_z_max":0.13798,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12333.0,"raw_peak_contact_force":1.5989,"subtask_id":"place_object","tcp_end":[0.50989,0.10799,0.20508],"tcp_start":[0.478,0.04669,0.12836],"tcp_to_object_dist_end":0.19078,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49056,0.09119,0.01602],"object_pos_start":[0.49056,0.09119,0.01602],"object_to_goal_dist_end":0.27071,"object_to_goal_dist_start":0.27071,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8281.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56033,0.19694,0.22169],"tcp_start":[0.50989,0.10799,0.20508],"tcp_to_object_dist_end":0.24156,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49056,0.09119,0.01602],"object_pos_start":[0.49056,0.09119,0.01602],"object_to_goal_dist_end":0.27071,"object_to_goal_dist_start":0.27071,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55578,0.19525,0.24346],"tcp_start":[0.56033,0.19694,0.22169],"tcp_to_object_dist_end":0.25848,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49056,0.09119,0.01602],"object_pos_start":[0.49056,0.09119,0.01602],"object_to_goal_dist_end":0.27071,"object_to_goal_dist_start":0.27071,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55471,0.19465,0.40076],"tcp_start":[0.55578,0.19525,0.24346],"tcp_to_object_dist_end":0.40354,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2b35d39beba75b46a5edd8e67b975c00ef2c88fb75a3753bdd32db5918adf9e2`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91525,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.pregrasp_height":0.15484,"descend_1.grasp_z_offset":0.01755,"descend_2.place_z_offset":-0.01051,"lift_1.lift_height":0.16259,"transport_1.transport_z_offset":0.11843},"optimized_scores":{"best_composite_score":0.11448,"best_fitness_score":0.54448,"best_task_score":0.15486},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2677.0,"contact_point_centroid":[0.55909,0.03019,-0.00235],"force_p95":0.12931,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.60089,"mean_force":0.13992,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54845,0.04138,0.20677]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.53549,-0.02064,-0.00113],"force_p95":0.30262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43693,"mean_force":0.05561,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52222,-0.0208,0.04396]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11429.0,"contact_point_centroid":[0.5284,-0.00189,0.10147],"force_p95":0.11104,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30257,"mean_force":0.07331,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52512,-0.02072,0.09954]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12234.0,"contact_point_centroid":[0.52844,-0.03946,0.10021],"force_p95":0.10684,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27728,"mean_force":0.06949,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52507,-0.02072,0.09874]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2046.0,"contact_point_centroid":[0.54006,0.01252,0.17607],"force_p95":0.142,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22084,"mean_force":0.10821,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53434,-0.00557,0.17999]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2034.0,"contact_point_centroid":[0.54,-0.02394,0.17591],"force_p95":0.14639,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20095,"mean_force":0.10877,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53427,-0.00591,0.17986]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02119,-0.00205],"force_p95":0.13637,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16856,"mean_force":0.12648,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52471,-0.02086,0.04364]},{"body_a":"world","body_b":"grasp_target","contact_count":1516.0,"contact_point_centroid":[0.53702,-0.02132,-0.00191],"force_p95":0.13479,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51361,-0.00929,0.24493]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4110.0,"contact_point_centroid":[0.52407,-0.00163,0.04503],"force_p95":0.07697,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12762,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52352,-0.02083,0.04225]},{"body_a":"world","body_b":"grasp_target","contact_count":1696.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52943,-0.01995,0.12093]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.55916,0.03019,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57641,0.1352,0.20466]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55916,0.03019,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59058,0.18818,0.19563]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.55916,0.03019,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58689,0.18676,0.28708]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4898.0,"contact_point_centroid":[0.52415,-0.03991,0.0441],"force_p95":0.06928,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08733,"mean_force":0.04467,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52353,-0.02083,0.04225]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2604.0,"contact_point_centroid":[0.54948,0.04401,0.2107],"force_p95":0.01117,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01633,"mean_force":0.01047,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5493,0.04401,0.20834]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4243.0,"contact_point_centroid":[0.57665,0.13507,0.207],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.0105,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57636,0.13506,0.20468]}],"total_contact_groups":17},"final_pose_error":0.04745,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.55916,0.03019,0.01602],"final_tcp_position":[0.58776,0.18697,0.36787],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.60089,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":380.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1516.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pregrasp","tcp_end":[0.52969,-0.01898,0.19103],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16519,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":424.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1696.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.53177,-0.02099,0.05199],"tcp_start":[0.52969,-0.01898,0.19103],"tcp_to_object_dist_end":0.0265,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53694,-0.02079,0.02582],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31644,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13394,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10808.0,"raw_peak_contact_force":0.16856,"tcp_end":[0.52349,-0.02083,0.04222],"tcp_start":[0.53177,-0.02099,0.05199],"tcp_to_object_dist_end":0.0212,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.54339,-0.02046,0.15007],"object_pos_start":[0.53694,-0.02079,0.02582],"object_to_goal_dist_end":0.26339,"object_to_goal_dist_start":0.31644,"object_z_max":0.14997,"peak_contact_force":0.16227,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23809.0,"raw_peak_contact_force":0.43693,"subtask_id":"lift_object","tcp_end":[0.53255,-0.0207,0.1757],"tcp_start":[0.52349,-0.02083,0.04222],"tcp_to_object_dist_end":0.02783,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55916,0.03019,0.01602],"object_pos_start":[0.54339,-0.02046,0.15007],"object_to_goal_dist_end":0.27979,"object_to_goal_dist_start":0.26339,"object_z_max":0.15686,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9361.0,"raw_peak_contact_force":1.60089,"subtask_id":"place_object","tcp_end":[0.55708,0.06824,0.22283],"tcp_start":[0.53255,-0.0207,0.1757],"tcp_to_object_dist_end":0.2103,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55916,0.03019,0.01602],"object_pos_start":[0.55916,0.03019,0.01602],"object_to_goal_dist_end":0.27979,"object_to_goal_dist_start":0.27979,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8243.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59438,0.18934,0.19473],"tcp_start":[0.55708,0.06824,0.22283],"tcp_to_object_dist_end":0.24189,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55916,0.03019,0.01602],"object_pos_start":[0.55916,0.03019,0.01602],"object_to_goal_dist_end":0.27979,"object_to_goal_dist_start":0.27979,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1013.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58915,0.18763,0.21529],"tcp_start":[0.59438,0.18934,0.19473],"tcp_to_object_dist_end":0.25573,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55916,0.03019,0.01602],"object_pos_start":[0.55916,0.03019,0.01602],"object_to_goal_dist_end":0.27979,"object_to_goal_dist_start":0.27979,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58776,0.18697,0.36787],"tcp_start":[0.58915,0.18763,0.21529],"tcp_to_object_dist_end":0.38626,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `530652a2467d9ac78fab654e7ed7fc5283ca1649270bc8f158e04c16074f9f95`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90741,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.pregrasp_height":0.1303,"descend_1.grasp_z_offset":0.01911,"descend_2.place_z_offset":0.0212,"lift_1.lift_height":0.13201,"transport_1.transport_z_offset":0.1093},"optimized_scores":{"best_composite_score":0.14924,"best_fitness_score":0.57924,"best_task_score":0.2271},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2453.0,"contact_point_centroid":[0.56992,0.0247,-0.00235],"force_p95":0.13642,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.4775,"mean_force":0.1427,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56158,0.02356,0.17632]},{"body_a":"world","body_b":"grasp_target","contact_count":155.0,"contact_point_centroid":[0.54408,-0.02813,-0.00116],"force_p95":0.26649,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42029,"mean_force":0.05383,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53051,-0.02845,0.04487]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9294.0,"contact_point_centroid":[0.53649,-0.00951,0.08928],"force_p95":0.10841,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29261,"mean_force":0.07148,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53349,-0.02838,0.08717]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10046.0,"contact_point_centroid":[0.53651,-0.04714,0.08789],"force_p95":0.10266,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27445,"mean_force":0.06723,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53341,-0.02838,0.08631]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3111.0,"contact_point_centroid":[0.54999,0.00414,0.14916],"force_p95":0.13197,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23676,"mean_force":0.08888,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54414,-0.0141,0.15035]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2803.0,"contact_point_centroid":[0.54972,-0.0328,0.14917],"force_p95":0.15845,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23002,"mean_force":0.09931,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54399,-0.01437,0.15012]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.0291,-0.00207],"force_p95":0.14181,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18386,"mean_force":0.12788,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53298,-0.02855,0.04457]},{"body_a":"world","body_b":"grasp_target","contact_count":1900.0,"contact_point_centroid":[0.5456,-0.02923,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51778,-0.01312,0.23214]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4104.0,"contact_point_centroid":[0.53244,-0.0093,0.04592],"force_p95":0.07792,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13328,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53178,-0.02851,0.04314]},{"body_a":"world","body_b":"grasp_target","contact_count":1376.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5378,-0.02764,0.10921]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.56999,0.02492,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59241,0.09157,0.18611]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56999,0.02492,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60786,0.12921,0.1885]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.56999,0.02492,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.60393,0.12817,0.28182]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4914.0,"contact_point_centroid":[0.5325,-0.0476,0.04497],"force_p95":0.07038,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07745,"mean_force":0.04466,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53178,-0.02851,0.04314]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2323.0,"contact_point_centroid":[0.56279,0.02548,0.18005],"force_p95":0.01133,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0162,"mean_force":0.01071,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56252,0.02548,0.17771]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4226.0,"contact_point_centroid":[0.59263,0.0917,0.18834],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01286,"mean_force":0.01054,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59247,0.0917,0.18612]}],"total_contact_groups":17},"final_pose_error":0.04351,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.56999,0.02492,0.01602],"final_tcp_position":[0.60485,0.12833,0.36464],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":273006.85898,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":476.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1900.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pregrasp","tcp_end":[0.53807,-0.02663,0.16604],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14025,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":344.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1376.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.54013,-0.02877,0.05321],"tcp_start":[0.53807,-0.02663,0.16604],"tcp_to_object_dist_end":0.02774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54552,-0.02855,0.02576],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.2606,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.1385,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10818.0,"raw_peak_contact_force":0.18386,"tcp_end":[0.53175,-0.02851,0.0431],"tcp_start":[0.54013,-0.02877,0.05321],"tcp_to_object_dist_end":0.02214,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.55306,-0.02844,0.12066],"object_pos_start":[0.54552,-0.02855,0.02576],"object_to_goal_dist_end":0.21661,"object_to_goal_dist_start":0.2606,"object_z_max":0.12055,"peak_contact_force":0.10865,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19495.0,"raw_peak_contact_force":0.42029,"subtask_id":"lift_object","tcp_end":[0.54065,-0.0284,0.14506],"tcp_start":[0.53175,-0.02851,0.0431],"tcp_to_object_dist_end":0.02737,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56999,0.02492,0.01602],"object_pos_start":[0.55306,-0.02844,0.12066],"object_to_goal_dist_end":0.22236,"object_to_goal_dist_start":0.21661,"object_z_max":0.12903,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10690.0,"raw_peak_contact_force":1.4775,"subtask_id":"place_object","tcp_end":[0.57099,0.04287,0.19025],"tcp_start":[0.54065,-0.0284,0.14506],"tcp_to_object_dist_end":0.17516,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56999,0.02492,0.01602],"object_pos_start":[0.56999,0.02492,0.01602],"object_to_goal_dist_end":0.22236,"object_to_goal_dist_start":0.22236,"object_z_max":0.01602,"peak_contact_force":273006.85898,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8226.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61184,0.13005,0.18763],"tcp_start":[0.57099,0.04287,0.19025],"tcp_to_object_dist_end":0.20556,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56999,0.02492,0.01602],"object_pos_start":[0.56999,0.02492,0.01602],"object_to_goal_dist_end":0.22236,"object_to_goal_dist_start":0.22236,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60634,0.1288,0.20811],"tcp_start":[0.61184,0.13005,0.18763],"tcp_to_object_dist_end":0.22139,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56999,0.02492,0.01602],"object_pos_start":[0.56999,0.02492,0.01602],"object_to_goal_dist_end":0.22236,"object_to_goal_dist_start":0.22236,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60485,0.12833,0.36464],"tcp_start":[0.60634,0.1288,0.20811],"tcp_to_object_dist_end":0.3653,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```