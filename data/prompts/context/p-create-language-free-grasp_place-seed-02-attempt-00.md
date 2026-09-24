## Search State

- **Seed**: 2
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2556 | 0.22 | ✅ accepted |

**Proposal policy**: task_score is 0.22 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`
- Frozen object start: [0.4761612134249316, -0.02015088565858767, 0.03]
- Frozen task target: [0.631422574059428, 0.1591915942135097, 0.1900150788948481]
- Goal object position: (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.4761612134249316, -0.02015088565858767, 0.03)
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
  frozen_object_start: [0.4762, -0.0202, 0.03]
  frozen_task_target: [0.6314, 0.1592, 0.19]
  frozen_object_starts: {'grasp_target': [0.4761612134249316, -0.02015088565858767, 0.03]}
  frozen_targets: {'place_target': [0.631422574059428, 0.1591915942135097, 0.1900150788948481]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a

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
| `object` | offset from object initial position (0.4761612134249316, -0.02015088565858767, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.631422574059428, 0.1591915942135097, 0.1900150788948481) | final destination targets |
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

## Current Skill (Q=0.256) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: object_at_goal
  target_entity: object
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
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_pre_grasp
- id: descend_1
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
- id: lift_1
  type: lift
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
- id: approach_2
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
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
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    placement_z_offset:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: object_at_goal
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
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **approach_2** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - placement_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.2], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.256
- **task_score** (E): 0.218
- **fitness_score**: 0.586  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1839 |
| descend_1 | 1.00 | 1.00 | 0.0954 |
| grasp_1 | 1.00 | 1.00 | 0.0114 |
| lift_1 | 1.00 | 1.00 | 0.0973 |
| approach_2 | 0.00 | 1.00 | 0.1020 |
| descend_2 | 0.00 | 1.00 | 0.0817 |
| release_1 | 1.00 | 1.00 | 0.0224 |
| retract_1 | 0.67 | 1.00 | 0.1593 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.490, -0.014, 0.121) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.490, -0.014, 0.121)→(0.488, -0.015, 0.026) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.488, -0.015, 0.026)→(0.480, -0.015, 0.018) | (0.493, -0.015, 0.026)→(0.492, -0.015, 0.025) | 0.281→0.281 | 1.00 / 45.667 | 0.150 | 0.190 |
| lift_1 | lift | 1.00 / step_budget | (0.480, -0.015, 0.018)→(0.488, -0.015, 0.115) | (0.492, -0.015, 0.025)→(0.509, -0.015, 0.113) | 0.281→0.239 | 1.00 / 26.667 | 0.074 | 0.796 |
| approach_2 | approach | 0.00 / step_budget | (0.488, -0.015, 0.115)→(0.539, 0.056, 0.163) | (0.509, -0.015, 0.113)→(0.521, 0.051, 0.016) | 0.239→0.229 | 1.00 / 8.333 | 94251.662 | 1.350 |
| descend_2 | descend | 0.00 / step_budget | (0.539, 0.056, 0.163)→(0.587, 0.119, 0.153) | (0.521, 0.051, 0.016)→(0.521, 0.051, 0.016) | 0.229→0.229 | 1.00 / 8.000 | 3249.689 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.587, 0.119, 0.153)→(0.581, 0.117, 0.175) | (0.521, 0.051, 0.016)→(0.521, 0.051, 0.016) | 0.229→0.229 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 0.67 / step_budget | (0.581, 0.117, 0.175)→(0.624, 0.163, 0.320) | (0.521, 0.051, 0.016)→(0.521, 0.051, 0.016) | 0.229→0.229 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.236
- phase_score: 0.244
- phase_breakdown.reach_pre_grasp_score: 0.505
- phase_breakdown.object_at_goal_score: 0.132
- grasp_place_fitness: 0.598

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.598
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.236
- **Median Q (composite search score)**: 0.255
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.235


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `dde525b5f1d1bd9dc458c18c8bb170b8849a392c0909c5e3e8e19baca2e18946`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3eaf951d4314ad541ffae42f4c615c856bb77d128e3ae1cab520a1988305ba67`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89024,"average_solve_count":164.0,"average_success_count":164.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10876,"descend_2.placement_z_offset":-0.0274,"lift_1.lift_height":0.1019},"optimized_scores":{"best_composite_score":0.24417,"best_fitness_score":0.57417,"best_task_score":0.19181},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2187.0,"contact_point_centroid":[0.50143,0.03996,-0.00236],"force_p95":0.16691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.37831,"mean_force":0.14303,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51157,0.02959,0.15861]},{"body_a":"world","body_b":"grasp_target","contact_count":129.0,"contact_point_centroid":[0.47427,-0.01967,-0.00108],"force_p95":0.60177,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73595,"mean_force":0.0762,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46264,-0.01973,0.02182]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9770.0,"contact_point_centroid":[0.46722,-0.00073,0.06612],"force_p95":0.1041,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27631,"mean_force":0.06424,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46525,-0.01966,0.0643]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10258.0,"contact_point_centroid":[0.46713,-0.03856,0.06446],"force_p95":0.10263,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26858,"mean_force":0.06188,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46512,-0.01966,0.06302]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4089.0,"contact_point_centroid":[0.48403,-0.02394,0.12407],"force_p95":0.17346,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24665,"mean_force":0.09572,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.48046,-0.00555,0.12581]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4425.0,"contact_point_centroid":[0.48513,0.01403,0.12501],"force_p95":0.15395,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24091,"mean_force":0.09502,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.48156,-0.00416,0.12696]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47614,-0.02002,-0.00203],"force_p95":0.13273,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16819,"mean_force":0.12554,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46486,-0.01979,0.02114]},{"body_a":"world","body_b":"grasp_target","contact_count":1824.0,"contact_point_centroid":[0.47616,-0.02015,-0.00192],"force_p95":0.13359,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48677,-0.00886,0.22454]},{"body_a":"world","body_b":"grasp_target","contact_count":2684.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47152,-0.01907,0.08465]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50142,0.04013,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.5512,0.07616,0.1643]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50142,0.04013,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57431,0.10503,0.16217]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50142,0.04013,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.59243,0.12486,0.25417]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5071.0,"contact_point_centroid":[0.46352,-0.00052,0.02296],"force_p95":0.06592,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08563,"mean_force":0.04287,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46372,-0.01977,0.02003]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5387.0,"contact_point_centroid":[0.46338,-0.03902,0.02244],"force_p95":0.06408,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08495,"mean_force":0.04122,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46372,-0.01977,0.02004]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2044.0,"contact_point_centroid":[0.51365,0.0316,0.16289],"force_p95":0.0114,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0164,"mean_force":0.0106,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51339,0.0316,0.16053]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4248.0,"contact_point_centroid":[0.55142,0.07609,0.16656],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01287,"mean_force":0.01049,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55112,0.07608,0.16431]}],"total_contact_groups":17},"final_pose_error":0.0635,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.50142,0.04013,0.01602],"final_tcp_position":[0.61513,0.14517,0.33027],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.37831,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":457.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1824.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.47473,-0.01823,0.14828],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12229,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":671.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2684.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47145,-0.01994,0.02758],"tcp_start":[0.47473,-0.01823,0.14828],"tcp_to_object_dist_end":0.00497,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47601,-0.01975,0.02587],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.2883,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13127,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12258.0,"raw_peak_contact_force":0.16819,"tcp_end":[0.46369,-0.01976,0.02001],"tcp_start":[0.47145,-0.01994,0.02758],"tcp_to_object_dist_end":0.01364,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.49176,-0.01955,0.11222],"object_pos_start":[0.47601,-0.01975,0.02587],"object_to_goal_dist_end":0.2398,"object_to_goal_dist_start":0.2883,"object_z_max":0.11213,"peak_contact_force":0.11535,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20157.0,"raw_peak_contact_force":0.73595,"tcp_end":[0.47123,-0.01964,0.11633],"tcp_start":[0.46369,-0.01976,0.02001],"tcp_to_object_dist_end":0.02094,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.04013,0.01602],"object_pos_start":[0.49176,-0.01955,0.11222],"object_to_goal_dist_end":0.24769,"object_to_goal_dist_start":0.2398,"object_z_max":0.11634,"peak_contact_force":0.12263,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12745.0,"raw_peak_contact_force":1.37831,"tcp_end":[0.52597,0.04544,0.17376],"tcp_start":[0.47123,-0.01964,0.11633],"tcp_to_object_dist_end":0.15973,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.04013,0.01602],"object_pos_start":[0.50142,0.04013,0.01602],"object_to_goal_dist_end":0.24769,"object_to_goal_dist_start":0.24769,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8248.0,"raw_peak_contact_force":0.12263,"subtask_id":"object_at_goal","tcp_end":[0.57858,0.1058,0.16035],"tcp_start":[0.52597,0.04544,0.17376],"tcp_to_object_dist_end":0.17634,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50142,0.04013,0.01602],"object_pos_start":[0.50142,0.04013,0.01602],"object_to_goal_dist_end":0.24769,"object_to_goal_dist_start":0.24769,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57265,0.10467,0.18225],"tcp_start":[0.57858,0.1058,0.16035],"tcp_to_object_dist_end":0.19202,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.04013,0.01602],"object_pos_start":[0.50142,0.04013,0.01602],"object_to_goal_dist_end":0.24769,"object_to_goal_dist_start":0.24769,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61513,0.14517,0.33027],"tcp_start":[0.57265,0.10467,0.18225],"tcp_to_object_dist_end":0.35031,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `92fc0f2bbc35407e7976a239cbab7bb266e8a517486aa3be6bd6666f4c63f38d`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89349,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07451,"descend_2.placement_z_offset":-0.01697,"lift_1.lift_height":0.10453},"optimized_scores":{"best_composite_score":0.26765,"best_fitness_score":0.59765,"best_task_score":0.23631},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1596.0,"contact_point_centroid":[0.50212,0.06369,-0.0025],"force_p95":0.26964,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.34405,"mean_force":0.15002,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50809,0.05142,0.14507]},{"body_a":"world","body_b":"grasp_target","contact_count":131.0,"contact_point_centroid":[0.45674,-0.02542,-0.00109],"force_p95":0.58148,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71739,"mean_force":0.07409,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44548,-0.02568,0.02285]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10462.0,"contact_point_centroid":[0.44986,-0.00666,0.06811],"force_p95":0.10241,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27118,"mean_force":0.06288,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.448,-0.02558,0.0663]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10767.0,"contact_point_centroid":[0.44978,-0.04452,0.06666],"force_p95":0.10221,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26824,"mean_force":0.0617,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44788,-0.02558,0.06514]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6332.0,"contact_point_centroid":[0.47497,0.02031,0.1249],"force_p95":0.1451,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24593,"mean_force":0.08955,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.47116,0.00208,0.12628]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5754.0,"contact_point_centroid":[0.47356,-0.01797,0.12447],"force_p95":0.16399,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24103,"mean_force":0.09309,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.47003,0.00051,0.12572]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45856,-0.02615,-0.00204],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18909,"mean_force":0.12667,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44765,-0.02577,0.02204]},{"body_a":"world","body_b":"grasp_target","contact_count":2260.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47827,-0.01191,0.20684]},{"body_a":"world","body_b":"grasp_target","contact_count":1968.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45439,-0.02509,0.06886]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50215,0.06391,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.54184,0.09948,0.13263]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50215,0.06391,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56098,0.12922,0.12178]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50215,0.06391,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58574,0.16115,0.2067]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5056.0,"contact_point_centroid":[0.44623,-0.00652,0.02358],"force_p95":0.06577,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0914,"mean_force":0.04282,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44656,-0.02573,0.02102]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5164.0,"contact_point_centroid":[0.44646,-0.04499,0.02297],"force_p95":0.06649,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08534,"mean_force":0.0431,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44656,-0.02573,0.02102]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1410.0,"contact_point_centroid":[0.51051,0.05421,0.14852],"force_p95":0.01214,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01564,"mean_force":0.01071,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51021,0.05421,0.14616]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4237.0,"contact_point_centroid":[0.54232,0.09953,0.13481],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0128,"mean_force":0.01051,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.54188,0.09953,0.13261]}],"total_contact_groups":17},"final_pose_error":0.04386,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.50215,0.06391,0.01602],"final_tcp_position":[0.61539,0.19355,0.27551],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9748.93908,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":566.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2260.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.45782,-0.02426,0.11404],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08805,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":492.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1968.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45403,-0.026,0.02803],"tcp_start":[0.45782,-0.02426,0.11404],"tcp_to_object_dist_end":0.00497,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45842,-0.02574,0.02583],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30334,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13459,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12020.0,"raw_peak_contact_force":0.18909,"tcp_end":[0.44653,-0.02573,0.02099],"tcp_start":[0.45403,-0.026,0.02803],"tcp_to_object_dist_end":0.01283,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.47382,-0.02552,0.11445],"object_pos_start":[0.45842,-0.02574,0.02583],"object_to_goal_dist_end":0.28118,"object_to_goal_dist_start":0.30334,"object_z_max":0.11435,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21360.0,"raw_peak_contact_force":0.71739,"tcp_end":[0.4538,-0.02558,0.11943],"tcp_start":[0.44653,-0.02573,0.02099],"tcp_to_object_dist_end":0.02062,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50215,0.06391,0.01602],"object_pos_start":[0.47382,-0.02552,0.11445],"object_to_goal_dist_end":0.21639,"object_to_goal_dist_start":0.28118,"object_z_max":0.11501,"peak_contact_force":9748.93908,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15092.0,"raw_peak_contact_force":1.34405,"tcp_end":[0.52047,0.0677,0.15141],"tcp_start":[0.4538,-0.02558,0.11943],"tcp_to_object_dist_end":0.13668,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50215,0.06391,0.01602],"object_pos_start":[0.50215,0.06391,0.01602],"object_to_goal_dist_end":0.21639,"object_to_goal_dist_start":0.21639,"object_z_max":0.01602,"peak_contact_force":9748.82241,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8237.0,"raw_peak_contact_force":0.12263,"subtask_id":"object_at_goal","tcp_end":[0.56567,0.13027,0.11967],"tcp_start":[0.52047,0.0677,0.15141],"tcp_to_object_dist_end":0.1385,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50215,0.06391,0.01602],"object_pos_start":[0.50215,0.06391,0.01602],"object_to_goal_dist_end":0.21639,"object_to_goal_dist_start":0.21639,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1015.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55914,0.12876,0.14201],"tcp_start":[0.56567,0.13027,0.11967],"tcp_to_object_dist_end":0.15273,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50215,0.06391,0.01602],"object_pos_start":[0.50215,0.06391,0.01602],"object_to_goal_dist_end":0.21639,"object_to_goal_dist_start":0.21639,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61539,0.19355,0.27551],"tcp_start":[0.55914,0.12876,0.14201],"tcp_to_object_dist_end":0.31139,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3b2449a94ded39f3d450008c4da002b4ddf87103ab7d1b86900d116c316ff53`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88344,"average_solve_count":163.0,"average_success_count":163.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06434,"descend_2.placement_z_offset":0.00982,"lift_1.lift_height":0.09695},"optimized_scores":{"best_composite_score":0.25511,"best_fitness_score":0.58511,"best_task_score":0.22549},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1904.0,"contact_point_centroid":[0.56063,0.05003,-0.00238],"force_p95":0.20589,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.32819,"mean_force":0.14358,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.56304,0.04253,0.15071]},{"body_a":"world","body_b":"grasp_target","contact_count":195.0,"contact_point_centroid":[0.54129,0.00072,-0.00157],"force_p95":0.70263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.93515,"mean_force":0.11682,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52871,0.00082,0.0147]},{"body_a":"grasp_target","body_b":"hand","contact_count":607.0,"contact_point_centroid":[0.54396,0.00103,0.09827],"force_p95":0.15231,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42556,"mean_force":0.12029,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53179,0.00069,0.05895]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5013.0,"contact_point_centroid":[0.54871,0.03444,0.11988],"force_p95":0.1606,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25685,"mean_force":0.10296,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.54471,0.01612,0.12102]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5032.0,"contact_point_centroid":[0.54805,-0.00324,0.1191],"force_p95":0.16177,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25626,"mean_force":0.09868,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.54409,0.01511,0.11999]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10005.0,"contact_point_centroid":[0.53341,0.01957,0.05463],"force_p95":0.09905,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2532,"mean_force":0.06109,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53112,0.0007,0.05286]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9386.0,"contact_point_centroid":[0.53352,-0.01826,0.05694],"force_p95":0.10098,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24955,"mean_force":0.06479,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5313,0.0007,0.0548]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54399,0.0009,-0.00252],"force_p95":0.18706,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21294,"mean_force":0.15793,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53154,0.00089,0.01387]},{"body_a":"grasp_target","body_b":"hand","contact_count":398.0,"contact_point_centroid":[0.54831,0.00172,0.05286],"force_p95":0.15389,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16977,"mean_force":0.13994,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53083,0.00088,0.01308]},{"body_a":"world","body_b":"grasp_target","contact_count":2604.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13005,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5174,0.00049,0.19977]},{"body_a":"world","body_b":"grasp_target","contact_count":3556.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53656,0.00099,0.05297]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.56043,0.0501,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59244,0.08752,0.16884]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56043,0.0501,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61196,0.11878,0.17994]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.56043,0.0501,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62404,0.13482,0.27363]},{"body_a":"grasp_target","body_b":"hand","contact_count":76.0,"contact_point_centroid":[0.5544,-0.00588,0.14811],"force_p95":0.1149,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12228,"mean_force":0.07781,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.53843,0.00438,0.11033]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4110.0,"contact_point_centroid":[0.53032,-0.0184,0.01522],"force_p95":0.07675,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08828,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53025,0.00087,0.01243]}],"total_contact_groups":20},"final_pose_error":0.03917,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.56043,0.0501,0.01602],"final_tcp_position":[0.64076,0.15155,0.3531],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273005.92409,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":652.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2604.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.53726,0.00099,0.10131],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07562,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":889.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3556.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53883,0.00103,0.02213],"tcp_start":[0.53726,0.00099,0.10131],"tcp_to_object_dist_end":0.00672,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54294,0.00067,0.02451],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25197,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.18383,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11684.0,"raw_peak_contact_force":0.21294,"tcp_end":[0.53022,0.00087,0.01239],"tcp_start":[0.53883,0.00103,0.02213],"tcp_to_object_dist_end":0.01757,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":607.0,"n_steps_budget":690.0,"object_pos_end":[0.5601,0.00066,0.11258],"object_pos_start":[0.54294,0.00067,0.02451],"object_to_goal_dist_end":0.19649,"object_to_goal_dist_start":0.25197,"object_z_max":0.11248,"peak_contact_force":0.10535,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20193.0,"raw_peak_contact_force":0.93515,"tcp_end":[0.53774,0.00061,0.10861],"tcp_start":[0.53022,0.00087,0.01239],"tcp_to_object_dist_end":0.02271,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56043,0.0501,0.01602],"object_pos_start":[0.5601,0.00066,0.11258],"object_to_goal_dist_end":0.22342,"object_to_goal_dist_start":0.19649,"object_z_max":0.11548,"peak_contact_force":273005.92409,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13710.0,"raw_peak_contact_force":1.32819,"tcp_end":[0.57149,0.05438,0.16429],"tcp_start":[0.53774,0.00061,0.10861],"tcp_to_object_dist_end":0.14874,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56043,0.0501,0.01602],"object_pos_start":[0.56043,0.0501,0.01602],"object_to_goal_dist_end":0.22342,"object_to_goal_dist_start":0.22342,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8240.0,"raw_peak_contact_force":0.12263,"subtask_id":"object_at_goal","tcp_end":[0.61605,0.1196,0.17918],"tcp_start":[0.57149,0.05438,0.16429],"tcp_to_object_dist_end":0.18586,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56043,0.0501,0.01602],"object_pos_start":[0.56043,0.0501,0.01602],"object_to_goal_dist_end":0.22342,"object_to_goal_dist_start":0.22342,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61038,0.1184,0.19949],"tcp_start":[0.61605,0.1196,0.17918],"tcp_to_object_dist_end":0.20204,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56043,0.0501,0.01602],"object_pos_start":[0.56043,0.0501,0.01602],"object_to_goal_dist_end":0.22342,"object_to_goal_dist_start":0.22342,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.64076,0.15155,0.3531],"tcp_start":[0.61038,0.1184,0.19949],"tcp_to_object_dist_end":0.36106,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```