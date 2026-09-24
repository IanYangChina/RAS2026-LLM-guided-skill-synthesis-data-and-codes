## Search State

- **Seed**: 9
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2191 | 0.15 | ❌ rejected |
| 0 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 0 | 0.1349 | 0.19 | ✅ accepted |

**Proposal policy**: task_score is 0.15 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`
- Frozen object start: [0.5370249203970084, -0.021318279091244466, 0.03]
- Frozen task target: [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]
- Goal object position: (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5370249203970084, -0.021318279091244466, 0.03)
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
  frozen_object_start: [0.537, -0.0213, 0.03]
  frozen_task_target: [0.6103, 0.2278, 0.2074]
  frozen_object_starts: {'grasp_target': [0.5370249203970084, -0.021318279091244466, 0.03]}
  frozen_targets: {'place_target': [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8

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
| `object` | offset from object initial position (0.5370249203970084, -0.021318279091244466, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6103148150051562, 0.2277534082920179, 0.2074111944405348) | final destination targets |
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

## Current Skill (Q=0.219) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_grasp_standoff
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: reach_place_standoff
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.7
phases:
- id: approach_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.005
    orientation:
      mode: keep_current
  subtask_id: reach_grasp_standoff
- id: descend_object
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
- id: grasp_object
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
- id: lift_object
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.005
    orientation:
      mode: keep_current
- id: approach_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.005
    orientation:
      mode: keep_current
  subtask_id: reach_place_standoff
- id: descend_goal
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
- id: release_object
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
- id: retract_goal
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.005
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.05], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_object** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.05], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **retract_goal** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.05], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.219
- **task_score** (E): 0.154
- **fitness_score**: 0.549  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.33 | 1.00 | 0.1811 |
| descend_object | 1.00 | 1.00 | 0.0858 |
| grasp_object | 1.00 | 1.00 | 0.0119 |
| lift_object | 1.00 | 1.00 | 0.1417 |
| approach_goal | 1.00 | 1.00 | 0.3194 |
| descend_goal | 1.00 | 1.00 | 0.0523 |
| release_object | 1.00 | 1.00 | 0.0203 |
| retract_goal | 1.00 | 1.00 | 0.0376 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.503, -0.012, 0.123) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_object | descend | 1.00 / step_budget | (0.503, -0.012, 0.123)→(0.508, -0.016, 0.037) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.508, -0.016, 0.037)→(0.500, -0.016, 0.029) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 38.000 | 0.148 | 0.205 |
| lift_object | lift | 1.00 / step_budget | (0.494, -0.016, 0.311)→(0.493, -0.016, 0.453) | (0.515, -0.016, 0.026)→(0.506, -0.016, 0.127) | 0.270→0.239 | 1.00 / 8.667 | 91001.340 | 1.596 |
| approach_goal | approach | 1.00 / step_budget | (0.493, -0.016, 0.453)→(0.607, 0.168, 0.226) | (0.499, -0.019, 0.016)→(0.499, -0.019, 0.016) | 0.285→0.285 | 1.00 / 8.333 | 3249.671 | 0.123 |
| descend_goal | descend | 1.00 / step_budget | (0.607, 0.168, 0.226)→(0.612, 0.177, 0.175) | (0.499, -0.019, 0.016)→(0.499, -0.019, 0.016) | 0.285→0.285 | 1.00 / 8.000 | 6499.216 | 0.123 |
| release_object | release | 1.00 / step_budget | (0.612, 0.177, 0.175)→(0.606, 0.175, 0.194) | (0.499, -0.019, 0.016)→(0.499, -0.019, 0.016) | 0.285→0.285 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_goal | retract | 1.00 / step_budget | (0.606, 0.175, 0.194)→(0.603, 0.174, 0.232) | (0.499, -0.019, 0.016)→(0.499, -0.019, 0.016) | 0.285→0.285 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.199
- phase_score: 0.742
- phase_breakdown.reach_place_standoff_score: 0.671
- phase_breakdown.reach_grasp_standoff_score: 0.907
- grasp_place_fitness: 0.578

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.578
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.199
- **Median Q (composite search score)**: 0.210
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.369


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `425c48e82220fc6e1b680086671cf7dd2586733ee271dec2149f96a25d69d0c6`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `58e88c03db0a62276863b22a53636bc89fead3e4bc7f4d35fd72d2282ace32bf`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.11848,"average_solve_count":211.0,"average_success_count":211.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.force_limit_approach":15.57003,"approach_goal.transport_speed":0.17637,"lift_object.lift_height":0.1642},"optimized_scores":{"best_composite_score":0.1989,"best_fitness_score":0.5289,"best_task_score":0.10605},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":7170.0,"contact_point_centroid":[0.51571,-0.03203,-0.0021],"force_p95":0.12287,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.63705,"mean_force":0.12844,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5151,-0.02023,0.32494]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11430.0,"contact_point_centroid":[0.52147,-0.03883,0.08768],"force_p95":0.13882,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41948,"mean_force":0.08153,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5176,-0.02028,0.08736]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10672.0,"contact_point_centroid":[0.52146,-0.00164,0.08865],"force_p95":0.14099,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33834,"mean_force":0.08497,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51758,-0.02028,0.08797]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53705,-0.02104,-0.00208],"force_p95":0.14864,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22636,"mean_force":0.12964,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52308,-0.02039,0.02507]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.53702,-0.02132,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51157,-0.00859,0.20609]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4073.0,"contact_point_centroid":[0.52311,-0.00117,0.02634],"force_p95":0.07883,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12705,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52183,-0.02037,0.02366]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_object","phase_type":"descend","tcp_position_centroid":[0.52537,-0.01828,0.07541]},{"body_a":"world","body_b":"grasp_target","contact_count":2496.0,"contact_point_centroid":[0.5153,-0.03229,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55867,0.09399,0.37089]},{"body_a":"world","body_b":"grasp_target","contact_count":580.0,"contact_point_centroid":[0.5153,-0.03229,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.60293,0.21615,0.23802]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5153,-0.03229,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6016,0.22072,0.21325]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.5153,-0.03229,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.59791,0.21907,0.24829]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4953.0,"contact_point_centroid":[0.52302,-0.03949,0.02544],"force_p95":0.07082,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08776,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52183,-0.02037,0.02367]},{"body_a":"left_finger","body_b":"right_finger","contact_count":7288.0,"contact_point_centroid":[0.51536,-0.02024,0.33843],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01577,"mean_force":0.01044,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51499,-0.02023,0.33605]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2668.0,"contact_point_centroid":[0.55896,0.0935,0.37362],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.01043,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55849,0.0935,0.37136]},{"body_a":"left_finger","body_b":"right_finger","contact_count":610.0,"contact_point_centroid":[0.60346,0.21619,0.24005],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.01058,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.60294,0.21617,0.23789]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.60427,0.22177,0.21223],"force_p95":0.01091,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01259,"mean_force":0.00994,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60377,0.22174,0.20976]}],"total_contact_groups":16},"final_pose_error":0.01298,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.5153,-0.03229,0.01602],"final_tcp_position":[0.5979,0.21902,0.26993],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273003.7744,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_grasp_standoff","tcp_end":[0.5229,-0.01552,0.1336],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10866,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53019,-0.02052,0.03313],"tcp_start":[0.5229,-0.01552,0.1336],"tcp_to_object_dist_end":0.00989,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53688,-0.02029,0.02572],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31612,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14272,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10826.0,"raw_peak_contact_force":0.22636,"tcp_end":[0.5218,-0.02037,0.02363],"tcp_start":[0.53019,-0.02052,0.03313],"tcp_to_object_dist_end":0.01522,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":2737.0,"n_steps_budget":1000.0,"object_pos_end":[0.52782,-0.02869,0.11798],"object_pos_start":[0.53688,-0.02029,0.02572],"object_to_goal_dist_end":0.28384,"object_to_goal_dist_start":0.31612,"object_z_max":0.14496,"peak_contact_force":273003.7744,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36560.0,"raw_peak_contact_force":1.63705,"tcp_end":[0.51569,-0.02028,0.48068],"tcp_start":[0.51593,-0.02024,0.32788],"tcp_to_object_dist_end":0.363,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":624.0,"n_steps_budget":1000.0,"object_pos_end":[0.5153,-0.03229,0.01602],"object_pos_start":[0.5153,-0.03229,0.01602],"object_to_goal_dist_end":0.33657,"object_to_goal_dist_start":0.33657,"object_z_max":0.01602,"peak_contact_force":9748.76897,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5164.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_place_standoff","tcp_end":[0.60219,0.21084,0.26333],"tcp_start":[0.51569,-0.02028,0.48068],"tcp_to_object_dist_end":0.35753,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":145.0,"n_steps_budget":1000.0,"object_pos_end":[0.5153,-0.03229,0.01602],"object_pos_start":[0.5153,-0.03229,0.01602],"object_to_goal_dist_end":0.33657,"object_to_goal_dist_start":0.33657,"object_z_max":0.01602,"peak_contact_force":9748.78639,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1190.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60526,0.22213,0.21361],"tcp_start":[0.60219,0.21084,0.26333],"tcp_to_object_dist_end":0.33446,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5153,-0.03229,0.01602],"object_pos_start":[0.5153,-0.03229,0.01602],"object_to_goal_dist_end":0.33657,"object_to_goal_dist_start":0.33657,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60036,0.22012,0.23263],"tcp_start":[0.60526,0.22213,0.21361],"tcp_to_object_dist_end":0.34332,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.5153,-0.03229,0.01602],"object_pos_start":[0.5153,-0.03229,0.01602],"object_to_goal_dist_end":0.33657,"object_to_goal_dist_start":0.33657,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5979,0.21902,0.26993],"tcp_start":[0.60036,0.22012,0.23263],"tcp_to_object_dist_end":0.36668,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88325,"average_solve_count":197.0,"average_success_count":197.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.force_limit_approach":13.51826,"approach_goal.transport_speed":0.15183,"lift_object.lift_height":0.12605},"optimized_scores":{"best_composite_score":0.21018,"best_fitness_score":0.54018,"best_task_score":0.15702},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":5593.0,"contact_point_centroid":[0.54233,-0.04199,-0.00214],"force_p95":0.12372,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.47021,"mean_force":0.12984,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51939,-0.02599,0.26717]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7801.0,"contact_point_centroid":[0.52854,-0.00755,0.09493],"force_p95":0.13782,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38106,"mean_force":0.09019,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52306,-0.02611,0.09384]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8155.0,"contact_point_centroid":[0.52851,-0.04458,0.09529],"force_p95":0.12772,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37332,"mean_force":0.0882,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52307,-0.02611,0.09457]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54571,-0.02894,-0.00223],"force_p95":0.18856,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24993,"mean_force":0.13898,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52854,-0.02627,0.04365]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3111.0,"contact_point_centroid":[0.53101,-0.00737,0.04575],"force_p95":0.10772,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14579,"mean_force":0.0649,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52732,-0.02624,0.04221]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.5456,-0.02923,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51364,-0.01086,0.21296]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_object","phase_type":"descend","tcp_position_centroid":[0.52961,-0.02312,0.09345]},{"body_a":"world","body_b":"grasp_target","contact_count":2060.0,"contact_point_centroid":[0.54235,-0.04254,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56935,0.06057,0.30546]},{"body_a":"world","body_b":"grasp_target","contact_count":584.0,"contact_point_centroid":[0.54235,-0.04254,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62295,0.1543,0.20604]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54235,-0.04254,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6221,0.15872,0.18215]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.54235,-0.04254,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.61767,0.15736,0.2171]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3410.0,"contact_point_centroid":[0.53162,-0.04524,0.04446],"force_p95":0.10291,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10479,"mean_force":0.06402,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52733,-0.02624,0.04222]},{"body_a":"left_finger","body_b":"right_finger","contact_count":5512.0,"contact_point_centroid":[0.51953,-0.02599,0.28105],"force_p95":0.01107,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01616,"mean_force":0.01053,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51918,-0.02598,0.27874]},{"body_a":"left_finger","body_b":"right_finger","contact_count":623.0,"contact_point_centroid":[0.62337,0.15434,0.20821],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01045,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62297,0.15433,0.20591]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2193.0,"contact_point_centroid":[0.5697,0.06058,0.30769],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.01047,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56936,0.06059,0.30544]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.62502,0.15957,0.18097],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01272,"mean_force":0.01011,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62467,0.15955,0.17866]}],"total_contact_groups":16},"final_pose_error":0.01314,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.54235,-0.04254,0.01602],"final_tcp_position":[0.61761,0.15731,0.23874],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":29888.77016,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_grasp_standoff","tcp_end":[0.52566,-0.01897,0.1509],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12688,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53549,-0.02646,0.05191],"tcp_start":[0.52566,-0.01897,0.1509],"tcp_to_object_dist_end":0.02793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54564,-0.02703,0.02526],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.25972,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.17535,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8321.0,"raw_peak_contact_force":0.24993,"tcp_end":[0.52729,-0.02624,0.04217],"tcp_start":[0.53549,-0.02646,0.05191],"tcp_to_object_dist_end":0.02496,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":2165.0,"n_steps_budget":810.0,"object_pos_end":[0.53163,-0.0269,0.12564],"object_pos_start":[0.54564,-0.02703,0.02526],"object_to_goal_dist_end":0.22287,"object_to_goal_dist_start":0.25972,"object_z_max":0.12597,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27061.0,"raw_peak_contact_force":1.47021,"tcp_end":[0.51905,-0.026,0.38298],"tcp_start":[0.52054,-0.02602,0.26939],"tcp_to_object_dist_end":0.25764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":515.0,"n_steps_budget":1000.0,"object_pos_end":[0.54235,-0.04254,0.01602],"object_pos_start":[0.54235,-0.04254,0.01602],"object_to_goal_dist_end":0.27771,"object_to_goal_dist_start":0.27771,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4253.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_place_standoff","tcp_end":[0.62138,0.14926,0.23064],"tcp_start":[0.51905,-0.026,0.38298],"tcp_to_object_dist_end":0.29849,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":146.0,"n_steps_budget":1000.0,"object_pos_end":[0.54235,-0.04254,0.01602],"object_pos_start":[0.54235,-0.04254,0.01602],"object_to_goal_dist_end":0.27771,"object_to_goal_dist_start":0.27771,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1207.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62637,0.15983,0.18255],"tcp_start":[0.62138,0.14926,0.23064],"tcp_to_object_dist_end":0.27522,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54235,-0.04254,0.01602],"object_pos_start":[0.54235,-0.04254,0.01602],"object_to_goal_dist_end":0.27771,"object_to_goal_dist_start":0.27771,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62059,0.15823,0.2015],"tcp_start":[0.62637,0.15983,0.18255],"tcp_to_object_dist_end":0.28431,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.54235,-0.04254,0.01602],"object_pos_start":[0.54235,-0.04254,0.01602],"object_to_goal_dist_end":0.27771,"object_to_goal_dist_start":0.27771,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61761,0.15731,0.23874],"tcp_start":[0.62059,0.15823,0.2015],"tcp_to_object_dist_end":0.30856,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`; realized-scene SHA-256: `776f3cbcac69f75f44cb26f0b1a492bbf1ced59f3c5fca79400c3f557c2ce565`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46286,-7e-05,0.03]},{"name":"goal","value":[0.61015,0.15287,0.12219]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.46286,-7e-05,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61015,0.15287,0.12219]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.00474,"average_solve_count":211.0,"average_success_count":211.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.force_limit_approach":15.0445,"approach_goal.transport_speed":0.28135,"lift_object.lift_height":0.1692},"optimized_scores":{"best_composite_score":0.24829,"best_fitness_score":0.57829,"best_task_score":0.1994},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":7075.0,"contact_point_centroid":[0.44119,0.01641,-0.0021],"force_p95":0.12303,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.68204,"mean_force":0.12931,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44413,-0.00027,0.33691]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12761.0,"contact_point_centroid":[0.44961,0.01847,0.08954],"force_p95":0.14076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32513,"mean_force":0.07816,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44671,-0.00025,0.08878]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13215.0,"contact_point_centroid":[0.44945,-0.01895,0.08506],"force_p95":0.13755,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29371,"mean_force":0.07363,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44672,-0.00025,0.08461]},{"body_a":"world","body_b":"grasp_target","contact_count":3804.0,"contact_point_centroid":[0.46286,-7e-05,-0.00196],"force_p95":0.12508,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47875,-6e-05,0.18932]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46283,-4e-05,-0.00201],"force_p95":0.12748,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13832,"mean_force":0.12422,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45165,-0.00021,0.02137]},{"body_a":"world","body_b":"grasp_target","contact_count":1520.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_object","phase_type":"descend","tcp_position_centroid":[0.45761,-0.00013,0.05377]},{"body_a":"world","body_b":"grasp_target","contact_count":2596.0,"contact_point_centroid":[0.44077,0.01671,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52017,0.07032,0.33994]},{"body_a":"world","body_b":"grasp_target","contact_count":676.0,"contact_point_centroid":[0.44077,0.01671,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.59911,0.14588,0.15508]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.44077,0.01671,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59812,0.14821,0.1286]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.44077,0.01671,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.59277,0.14673,0.1646]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4146.0,"contact_point_centroid":[0.45078,0.01907,0.02263],"force_p95":0.07654,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09392,"mean_force":0.0521,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45055,-0.00022,0.02033]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5332.0,"contact_point_centroid":[0.45017,-0.01926,0.02268],"force_p95":0.0629,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08318,"mean_force":0.04075,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45055,-0.00022,0.02033]},{"body_a":"left_finger","body_b":"right_finger","contact_count":7141.0,"contact_point_centroid":[0.44436,-0.00027,0.34941],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01618,"mean_force":0.01056,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44403,-0.00027,0.34715]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2755.0,"contact_point_centroid":[0.52042,0.07019,0.34256],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.01049,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52003,0.07018,0.34025]},{"body_a":"left_finger","body_b":"right_finger","contact_count":715.0,"contact_point_centroid":[0.59971,0.14589,0.15743],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01272,"mean_force":0.01053,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.5991,0.14588,0.15513]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.60146,0.1491,0.12674],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.00991,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60116,0.14908,0.12458]}],"total_contact_groups":16},"final_pose_error":0.01263,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.44077,0.01671,0.01602],"final_tcp_position":[0.59261,0.14667,0.18631],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":9748.73914,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":952.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3804.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_grasp_standoff","tcp_end":[0.46015,-0.0001,0.08407],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.05811,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":380.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1520.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45806,-0.00013,0.02742],"tcp_start":[0.46015,-0.0001,0.08407],"tcp_to_object_dist_end":0.005,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46271,1e-05,0.02593],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23317,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12737,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11278.0,"raw_peak_contact_force":0.13832,"tcp_end":[0.45052,-0.00022,0.0203],"tcp_start":[0.45806,-0.00013,0.02742],"tcp_to_object_dist_end":0.01343,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":2766.0,"n_steps_budget":1000.0,"object_pos_end":[0.45938,0.0069,0.13786],"object_pos_start":[0.46271,1e-05,0.02593],"object_to_goal_dist_end":0.21044,"object_to_goal_dist_start":0.23317,"object_z_max":0.15025,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40192.0,"raw_peak_contact_force":1.68204,"tcp_end":[0.44456,-0.0003,0.49568],"tcp_start":[0.44495,-0.00026,0.33689],"tcp_to_object_dist_end":0.3582,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":649.0,"n_steps_budget":1000.0,"object_pos_end":[0.44077,0.01671,0.01602],"object_pos_start":[0.44077,0.01671,0.01602],"object_to_goal_dist_end":0.24187,"object_to_goal_dist_start":0.24187,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5351.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_place_standoff","tcp_end":[0.59741,0.14284,0.1838],"tcp_start":[0.44456,-0.0003,0.49568],"tcp_to_object_dist_end":0.2619,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":169.0,"n_steps_budget":1000.0,"object_pos_end":[0.44077,0.01671,0.01602],"object_pos_start":[0.44077,0.01671,0.01602],"object_to_goal_dist_end":0.24187,"object_to_goal_dist_start":0.24187,"object_z_max":0.01602,"peak_contact_force":9748.73914,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1391.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60309,0.1495,0.12813],"tcp_start":[0.59741,0.14284,0.1838],"tcp_to_object_dist_end":0.23781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.44077,0.01671,0.01602],"object_pos_start":[0.44077,0.01671,0.01602],"object_to_goal_dist_end":0.24187,"object_to_goal_dist_start":0.24187,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59629,0.14768,0.14835],"tcp_start":[0.60309,0.1495,0.12813],"tcp_to_object_dist_end":0.24259,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.44077,0.01671,0.01602],"object_pos_start":[0.44077,0.01671,0.01602],"object_to_goal_dist_end":0.24187,"object_to_goal_dist_start":0.24187,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59261,0.14667,0.18631],"tcp_start":[0.59629,0.14768,0.14835],"tcp_to_object_dist_end":0.26257,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```