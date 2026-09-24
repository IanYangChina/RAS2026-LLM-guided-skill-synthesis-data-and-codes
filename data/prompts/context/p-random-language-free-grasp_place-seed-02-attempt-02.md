## Search State

- **Seed**: 2
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 11 | 0.3386 | 1.00 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | contact_detected | time_limit | pose_tolerance | 15 | -0.2570 | 0.39 | ✅ accepted |
| 0 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0 | 0.1073 | 0.16 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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

## Current Skill (Q=0.339) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.3
- id: reach_goal
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
    - 0.12
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    approach_offset_z:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_object
- id: descend_grasp
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_offset_z:
      type: scalar
      range:
      - 0.0
      - 0.04
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
- id: grasp
  type: grasp
  control: impedance_control
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
      mode: none
- id: lift
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
    - 0.15
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
    tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
- id: place_at_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    place_offset_z:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.12], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
    - tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_offset_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
    - tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **place_at_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
    - tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: 0.339
- **task_score** (E): 1.000
- **fitness_score**: 0.979  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.640

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1263 |
| descend_grasp | 1.00 | 1.00 | 0.1485 |
| grasp | 1.00 | 1.00 | 0.0114 |
| lift | 1.00 | 1.00 | 0.1033 |
| place_at_goal | 1.00 | 1.00 | 0.2401 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, -0.011, 0.179) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.493, -0.011, 0.179)→(0.488, -0.015, 0.031) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.488, -0.015, 0.031)→(0.480, -0.015, 0.022) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 44.667 | 0.144 | 0.191 |
| lift | lift | 1.00 / step_budget | (0.480, -0.015, 0.022)→(0.477, -0.015, 0.126) | (0.493, -0.015, 0.026)→(0.496, -0.015, 0.126) | 0.281→0.244 | 1.00 / 24.667 | 64.118 | 0.863 |
| place_at_goal | approach | 1.00 / step_budget | (0.477, -0.015, 0.126)→(0.625, 0.164, 0.167) | (0.496, -0.015, 0.126)→(0.633, 0.165, 0.151) | 0.244→0.019 | 1.00 / 33.333 | 0.107 | 0.188 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.024
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.679
- phase_breakdown.reach_goal_score: 0.690
- phase_breakdown.reach_object_score: 0.655
- grasp_place_fitness: 0.982

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.982
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.341
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.332


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.2451,"average_solve_count":102.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.14975,"approach_object.speed":0.20399,"approach_object.tolerance":0.0415,"descend_grasp.descend_offset_z":0.00641,"descend_grasp.speed":0.11288,"lift.lift_height":0.13456,"lift.speed":0.19331,"lift.tolerance":0.02943,"place_at_goal.place_offset_z":0.0185,"place_at_goal.speed":0.18485,"place_at_goal.tolerance":0.03766},"optimized_scores":{"best_composite_score":0.34072,"best_fitness_score":0.98072,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":59.0,"contact_point_centroid":[0.47287,-0.01951,-0.00145],"force_p95":0.74305,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.75148,"mean_force":0.24808,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46269,-0.01961,0.02828]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3226.0,"contact_point_centroid":[0.46267,-0.00044,0.07502],"force_p95":0.10769,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34203,"mean_force":0.06611,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46125,-0.01957,0.07235]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3546.0,"contact_point_centroid":[0.46271,-0.03861,0.07403],"force_p95":0.10251,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33218,"mean_force":0.06129,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46123,-0.01957,0.07211]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8746.0,"contact_point_centroid":[0.54821,0.05195,0.16613],"force_p95":0.11514,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18567,"mean_force":0.08117,"phase_index":4.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.54486,0.07077,0.16506]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02003,-0.00204],"force_p95":0.13642,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18552,"mean_force":0.12645,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46521,-0.01967,0.02822]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10139.0,"contact_point_centroid":[0.55174,0.09356,0.16754],"force_p95":0.10372,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1514,"mean_force":0.06573,"phase_index":4.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.54891,0.07505,0.16674]},{"body_a":"world","body_b":"grasp_target","contact_count":516.0,"contact_point_centroid":[0.47616,-0.02015,-0.00176],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12357,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49116,-0.00674,0.25677]},{"body_a":"world","body_b":"grasp_target","contact_count":3476.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47492,-0.01718,0.11714]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5068.0,"contact_point_centroid":[0.46378,-0.0004,0.02971],"force_p95":0.06569,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09355,"mean_force":0.04291,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46409,-0.01964,0.02712]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5368.0,"contact_point_centroid":[0.46369,-0.0389,0.0292],"force_p95":0.06476,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0877,"mean_force":0.04139,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46409,-0.01964,0.02712]}],"total_contact_groups":10},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62648,0.14917,0.17478],"final_tcp_position":[0.61942,0.14907,0.19623],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.75148,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":130.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12261,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":516.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.48124,-0.01444,0.20871],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":869.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3476.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.47176,-0.01982,0.0347],"tcp_start":[0.48124,-0.01444,0.20871],"tcp_to_object_dist_end":0.00974,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01967,0.02583],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28826,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13439,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12236.0,"raw_peak_contact_force":0.18552,"tcp_end":[0.46406,-0.01964,0.02709],"tcp_start":[0.47176,-0.01982,0.0347],"tcp_to_object_dist_end":0.01204,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":194.0,"n_steps_budget":600.0,"object_pos_end":[0.48027,-0.01943,0.1271],"object_pos_start":[0.47603,-0.01967,0.02583],"object_to_goal_dist_end":0.2423,"object_to_goal_dist_start":0.28826,"object_z_max":0.12662,"peak_contact_force":0.10768,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6831.0,"raw_peak_contact_force":0.75148,"tcp_end":[0.46132,-0.01954,0.13202],"tcp_start":[0.46406,-0.01964,0.02709],"tcp_to_object_dist_end":0.01958,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":658.0,"n_steps_budget":1000.0,"object_pos_end":[0.62648,0.14917,0.17478],"object_pos_start":[0.48027,-0.01943,0.1271],"object_to_goal_dist_end":0.01889,"object_to_goal_dist_start":0.2423,"object_z_max":0.17473,"peak_contact_force":0.11847,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18885.0,"raw_peak_contact_force":0.18567,"subtask_id":"reach_goal","tcp_end":[0.61942,0.14907,0.19623],"tcp_start":[0.46132,-0.01954,0.13202],"tcp_to_object_dist_end":0.02258,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.14286,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.11068,"approach_object.speed":0.12128,"approach_object.tolerance":0.02795,"descend_grasp.descend_offset_z":0.0039,"descend_grasp.speed":0.13359,"lift.lift_height":0.13644,"lift.speed":0.11093,"lift.tolerance":0.02893,"place_at_goal.place_offset_z":0.01181,"place_at_goal.speed":0.22882,"place_at_goal.tolerance":0.03091},"optimized_scores":{"best_composite_score":0.34152,"best_fitness_score":0.98152,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.45562,-0.02519,-0.0015],"force_p95":0.7082,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72774,"mean_force":0.27752,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44569,-0.02556,0.02656]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3707.0,"contact_point_centroid":[0.4449,-0.00632,0.07678],"force_p95":0.09803,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31047,"mean_force":0.06065,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44409,-0.02548,0.0742]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4060.0,"contact_point_centroid":[0.44491,-0.04458,0.07636],"force_p95":0.09187,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29325,"mean_force":0.05624,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44407,-0.02548,0.07452]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02613,-0.00206],"force_p95":0.1405,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20026,"mean_force":0.12755,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44804,-0.02564,0.02652]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11030.0,"contact_point_centroid":[0.53758,0.0743,0.12499],"force_p95":0.11003,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19906,"mean_force":0.07024,"phase_index":4.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.53599,0.09336,0.12329]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12947.0,"contact_point_centroid":[0.5417,0.11785,0.12457],"force_p95":0.09486,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15452,"mean_force":0.05492,"phase_index":4.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.54057,0.09917,0.12295]},{"body_a":"world","body_b":"grasp_target","contact_count":744.0,"contact_point_centroid":[0.45856,-0.02632,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12328,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48337,-0.00984,0.23693]},{"body_a":"world","body_b":"grasp_target","contact_count":2700.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.45824,-0.0233,0.09746]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4811.0,"contact_point_centroid":[0.44693,-0.00637,0.02778],"force_p95":0.06806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09788,"mean_force":0.04493,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44695,-0.02561,0.0255]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5420.0,"contact_point_centroid":[0.4464,-0.04484,0.02718],"force_p95":0.06508,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08421,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44695,-0.02561,0.0255]}],"total_contact_groups":10},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62141,0.19596,0.10166],"final_tcp_position":[0.61707,0.19552,0.11771],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.72774,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":187.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":744.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46536,-0.0207,0.16924],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14349,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":675.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2700.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45439,-0.02587,0.03254],"tcp_start":[0.46536,-0.0207,0.16924],"tcp_to_object_dist_end":0.00775,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.0256,0.02579],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30324,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13738,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12031.0,"raw_peak_contact_force":0.20026,"tcp_end":[0.44692,-0.0256,0.02547],"tcp_start":[0.45439,-0.02587,0.03254],"tcp_to_object_dist_end":0.01152,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":203.0,"n_steps_budget":780.0,"object_pos_end":[0.46173,-0.02537,0.1314],"object_pos_start":[0.45844,-0.0256,0.02579],"object_to_goal_dist_end":0.28847,"object_to_goal_dist_start":0.30324,"object_z_max":0.1309,"peak_contact_force":0.10311,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7827.0,"raw_peak_contact_force":0.72774,"tcp_end":[0.44407,-0.02544,0.13231],"tcp_start":[0.44692,-0.0256,0.02547],"tcp_to_object_dist_end":0.01768,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":695.0,"n_steps_budget":1000.0,"object_pos_end":[0.62141,0.19596,0.10166],"object_pos_start":[0.46173,-0.02537,0.1314],"object_to_goal_dist_end":0.01953,"object_to_goal_dist_start":0.28847,"object_z_max":0.13272,"peak_contact_force":0.08532,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23977.0,"raw_peak_contact_force":0.19906,"subtask_id":"reach_goal","tcp_end":[0.61707,0.19552,0.11771],"tcp_start":[0.44407,-0.02544,0.13231],"tcp_to_object_dist_end":0.01663,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.37931,"average_solve_count":87.0,"average_success_count":87.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.10056,"approach_object.speed":0.16479,"approach_object.tolerance":0.0212,"descend_grasp.descend_offset_z":0.00089,"descend_grasp.speed":0.18249,"lift.lift_height":0.1274,"lift.speed":0.2186,"lift.tolerance":0.04279,"place_at_goal.place_offset_z":0.01133,"place_at_goal.speed":0.19369,"place_at_goal.tolerance":0.0342},"optimized_scores":{"best_composite_score":0.33349,"best_fitness_score":0.97349,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":72.0,"contact_point_centroid":[0.54009,0.00067,-0.00171],"force_p95":1.07245,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.10841,"mean_force":0.35249,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52849,0.00083,0.01626]},{"body_a":"grasp_target","body_b":"hand","contact_count":195.0,"contact_point_centroid":[0.54465,0.00224,0.09983],"force_p95":0.18058,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.57773,"mean_force":0.09544,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52662,0.00079,0.06154]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3019.0,"contact_point_centroid":[0.52863,-0.01827,0.06056],"force_p95":0.10625,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34145,"mean_force":0.069,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52664,0.00079,0.05794]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3367.0,"contact_point_centroid":[0.52865,0.01971,0.05787],"force_p95":0.10503,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31704,"mean_force":0.06322,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52667,0.00079,0.05577]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54414,0.00094,-0.00229],"force_p95":0.16232,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18754,"mean_force":0.14255,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53141,0.00089,0.01635]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6837.0,"contact_point_centroid":[0.58739,0.05952,0.15176],"force_p95":0.12114,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18022,"mean_force":0.08812,"phase_index":4.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.58352,0.0783,0.15076]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7980.0,"contact_point_centroid":[0.59102,0.10091,0.15383],"force_p95":0.11078,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17473,"mean_force":0.07624,"phase_index":4.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.58668,0.08244,0.15295]},{"body_a":"world","body_b":"grasp_target","contact_count":784.0,"contact_point_centroid":[0.54431,0.00113,-0.00184],"force_p95":0.13755,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12325,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51581,0.00042,0.23105]},{"body_a":"world","body_b":"grasp_target","contact_count":3832.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53464,0.00094,0.08162]},{"body_a":"grasp_target","body_b":"hand","contact_count":372.0,"contact_point_centroid":[0.54801,-0.00347,0.05416],"force_p95":0.08842,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11637,"mean_force":0.08056,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53046,0.00087,0.01529]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4884.0,"contact_point_centroid":[0.53082,0.01995,0.01673],"force_p95":0.06774,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09312,"mean_force":0.04492,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53013,0.00087,0.01491]},{"body_a":"grasp_target","body_b":"hand","contact_count":8.0,"contact_point_centroid":[0.54583,-0.01358,0.15155],"force_p95":0.0891,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09079,"mean_force":0.055,"phase_index":4.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.52774,0.00145,0.11411]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4108.0,"contact_point_centroid":[0.53083,-0.01833,0.01764],"force_p95":0.0762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08857,"mean_force":0.05159,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53012,0.00087,0.01491]}],"total_contact_groups":13},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.65246,0.14846,0.17518],"final_tcp_position":[0.63745,0.14836,0.18852],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":192.14307,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":197.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":784.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53309,0.00087,0.15838],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13283,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":958.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3832.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5387,0.00103,0.02465],"tcp_start":[0.53309,0.00087,0.15838],"tcp_to_object_dist_end":0.00577,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54344,0.00074,0.02511],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25133,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.16144,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11164.0,"raw_peak_contact_force":0.18754,"tcp_end":[0.53009,0.00086,0.01487],"tcp_start":[0.5387,0.00103,0.02465],"tcp_to_object_dist_end":0.01682,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":195.0,"n_steps_budget":600.0,"object_pos_end":[0.54657,0.00082,0.11999],"object_pos_start":[0.54344,0.00074,0.02511],"object_to_goal_dist_end":0.2,"object_to_goal_dist_start":0.25133,"object_z_max":0.11953,"peak_contact_force":192.14307,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6653.0,"raw_peak_contact_force":1.10841,"tcp_end":[0.52654,0.00079,0.11284],"tcp_start":[0.53009,0.00086,0.01487],"tcp_to_object_dist_end":0.02127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":579.0,"n_steps_budget":1000.0,"object_pos_end":[0.65246,0.14846,0.17518],"object_pos_start":[0.54657,0.00082,0.11999],"object_to_goal_dist_end":0.01923,"object_to_goal_dist_start":0.2,"object_z_max":0.1751,"peak_contact_force":0.11792,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14825.0,"raw_peak_contact_force":0.18022,"subtask_id":"reach_goal","tcp_end":[0.63745,0.14836,0.18852],"tcp_start":[0.52654,0.00079,0.11284],"tcp_to_object_dist_end":0.02008,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```