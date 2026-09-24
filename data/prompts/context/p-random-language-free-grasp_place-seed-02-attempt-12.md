## Search State

- **Seed**: 2
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 11 | 0.3168 | 0.95 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 11 | 0.3112 | 0.94 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 12 | 0.2565 | 0.95 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 12 | -0.4230 | 0.16 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 13 | -0.4730 | 0.16 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.95). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.317) — your mutation base

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

- **Composite score**: 0.317
- **task_score** (E): 0.953
- **fitness_score**: 0.957  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.640

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1289 |
| descend_grasp | 1.00 | 1.00 | 0.1422 |
| grasp | 1.00 | 1.00 | 0.0114 |
| lift | 1.00 | 1.00 | 0.1140 |
| place_at_goal | 1.00 | 1.00 | 0.2351 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, -0.012, 0.176) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.493, -0.012, 0.176)→(0.488, -0.015, 0.034) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.488, -0.015, 0.034)→(0.480, -0.015, 0.026) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 44.667 | 0.134 | 0.179 |
| lift | lift | 1.00 / step_budget | (0.480, -0.015, 0.026)→(0.477, -0.015, 0.140) | (0.493, -0.015, 0.026)→(0.496, -0.015, 0.137) | 0.281→0.240 | 1.00 / 30.333 | 0.103 | 0.767 |
| place_at_goal | approach | 1.00 / step_budget | (0.477, -0.015, 0.140)→(0.624, 0.164, 0.169) | (0.496, -0.015, 0.137)→(0.633, 0.164, 0.151) | 0.240→0.019 | 1.00 / 29.667 | 0.129 | 0.240 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.241
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.609
- phase_breakdown.reach_goal_score: 0.689
- phase_breakdown.reach_object_score: 0.421
- grasp_place_fitness: 0.982

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.982
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.338
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.348


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83969,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.105,"approach_object.speed":0.11546,"approach_object.tolerance":0.0288,"descend_grasp.descend_offset_z":0.00624,"descend_grasp.speed":0.11239,"lift.lift_height":0.17068,"lift.speed":0.06323,"lift.tolerance":0.02331,"place_at_goal.place_offset_z":0.00771,"place_at_goal.speed":0.26985,"place_at_goal.tolerance":0.034},"optimized_scores":{"best_composite_score":0.27077,"best_fitness_score":0.91077,"best_task_score":0.86019},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":66.0,"contact_point_centroid":[0.47342,-0.01984,-0.00149],"force_p95":0.58364,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66779,"mean_force":0.25565,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46301,-0.01962,0.02791]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5216.0,"contact_point_centroid":[0.46165,-0.00038,0.09529],"force_p95":0.09,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29491,"mean_force":0.05877,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46102,-0.01955,0.09283]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5692.0,"contact_point_centroid":[0.46168,-0.03864,0.09485],"force_p95":0.08394,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29193,"mean_force":0.05462,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.461,-0.01955,0.09307]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8579.0,"contact_point_centroid":[0.53941,0.0435,0.17708],"force_p95":0.11069,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25422,"mean_force":0.07252,"phase_index":4.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.53685,0.06231,0.17607]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9207.0,"contact_point_centroid":[0.54563,0.08759,0.17764],"force_p95":0.10119,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19072,"mean_force":0.06319,"phase_index":4.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.54316,0.06901,0.17691]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02003,-0.00204],"force_p95":0.13636,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18547,"mean_force":0.12643,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46516,-0.01967,0.02797]},{"body_a":"world","body_b":"grasp_target","contact_count":756.0,"contact_point_centroid":[0.47616,-0.02015,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12327,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48989,-0.00754,0.23451]},{"body_a":"world","body_b":"grasp_target","contact_count":2656.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47374,-0.01787,0.09572]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5068.0,"contact_point_centroid":[0.46374,-0.0004,0.02951],"force_p95":0.06573,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0934,"mean_force":0.0429,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46403,-0.01964,0.02686]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5397.0,"contact_point_centroid":[0.46361,-0.0389,0.029],"force_p95":0.06471,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0878,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46404,-0.01964,0.02686]}],"total_contact_groups":10},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62778,0.14804,0.17071],"final_tcp_position":[0.61835,0.14813,0.18751],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.66779,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":190.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":756.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47906,-0.01587,0.16423],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13831,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":664.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2656.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.4717,-0.01982,0.03444],"tcp_start":[0.47906,-0.01587,0.16423],"tcp_to_object_dist_end":0.00954,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01966,0.02583],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28826,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13446,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12265.0,"raw_peak_contact_force":0.18547,"tcp_end":[0.46401,-0.01964,0.02683],"tcp_start":[0.4717,-0.01982,0.03444],"tcp_to_object_dist_end":0.01207,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":280.0,"n_steps_budget":1000.0,"object_pos_end":[0.47783,-0.01941,0.16433],"object_pos_start":[0.47603,-0.01966,0.02583],"object_to_goal_dist_end":0.23696,"object_to_goal_dist_start":0.28826,"object_z_max":0.16385,"peak_contact_force":0.09977,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10974.0,"raw_peak_contact_force":0.66779,"tcp_end":[0.46101,-0.01953,0.16771],"tcp_start":[0.46401,-0.01964,0.02683],"tcp_to_object_dist_end":0.01715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":566.0,"n_steps_budget":1000.0,"object_pos_end":[0.62778,0.14804,0.17071],"object_pos_start":[0.47783,-0.01941,0.16433],"object_to_goal_dist_end":0.02259,"object_to_goal_dist_start":0.23696,"object_z_max":0.1707,"peak_contact_force":0.11656,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17786.0,"raw_peak_contact_force":0.25422,"subtask_id":"reach_goal","tcp_end":[0.61835,0.14813,0.18751],"tcp_start":[0.46101,-0.01953,0.16771],"tcp_to_object_dist_end":0.01926,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.56098,"average_solve_count":82.0,"average_success_count":82.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.13457,"approach_object.speed":0.27929,"approach_object.tolerance":0.01886,"descend_grasp.descend_offset_z":0.00446,"descend_grasp.speed":0.22717,"lift.lift_height":0.11908,"lift.speed":0.16059,"lift.tolerance":0.02999,"place_at_goal.place_offset_z":0.01651,"place_at_goal.speed":0.29679,"place_at_goal.tolerance":0.03083},"optimized_scores":{"best_composite_score":0.34154,"best_fitness_score":0.98154,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.45561,-0.0252,-0.00146],"force_p95":0.73974,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.7942,"mean_force":0.26919,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44563,-0.02556,0.02729]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3083.0,"contact_point_centroid":[0.445,-0.00632,0.06908],"force_p95":0.0985,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34571,"mean_force":0.06094,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44425,-0.02549,0.06658]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3347.0,"contact_point_centroid":[0.44501,-0.04462,0.06852],"force_p95":0.0927,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32604,"mean_force":0.05696,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44424,-0.02549,0.06665]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9468.0,"contact_point_centroid":[0.53862,0.07389,0.11844],"force_p95":0.12074,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26032,"mean_force":0.07905,"phase_index":4.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.53562,0.09285,0.11738]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02613,-0.00206],"force_p95":0.14016,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19333,"mean_force":0.12747,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44806,-0.02565,0.02721]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12524.0,"contact_point_centroid":[0.54137,0.11673,0.11915],"force_p95":0.09806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1892,"mean_force":0.05519,"phase_index":4.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.53989,0.09828,0.11754]},{"body_a":"world","body_b":"grasp_target","contact_count":604.0,"contact_point_centroid":[0.45856,-0.02632,-0.00179],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12343,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48409,-0.00947,0.24805]},{"body_a":"world","body_b":"grasp_target","contact_count":2788.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.45899,-0.02296,0.10903]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4812.0,"contact_point_centroid":[0.44694,-0.00637,0.02845],"force_p95":0.06801,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09789,"mean_force":0.04493,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44696,-0.02561,0.02618]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5419.0,"contact_point_centroid":[0.44642,-0.04485,0.02786],"force_p95":0.06502,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08374,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44697,-0.02561,0.02619]}],"total_contact_groups":10},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62526,0.19691,0.10522],"final_tcp_position":[0.61759,0.19632,0.12102],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.7942,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":152.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":604.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46674,-0.02001,0.19197],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16627,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":697.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2788.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.4544,-0.02587,0.0332],"tcp_start":[0.46674,-0.02001,0.19197],"tcp_to_object_dist_end":0.00832,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02561,0.02579],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30324,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13712,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12031.0,"raw_peak_contact_force":0.19333,"tcp_end":[0.44694,-0.02561,0.02616],"tcp_start":[0.4544,-0.02587,0.0332],"tcp_to_object_dist_end":0.01151,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":167.0,"n_steps_budget":600.0,"object_pos_end":[0.46162,-0.02541,0.1127],"object_pos_start":[0.45844,-0.02561,0.02579],"object_to_goal_dist_end":0.28806,"object_to_goal_dist_start":0.30324,"object_z_max":0.1122,"peak_contact_force":0.10081,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6490.0,"raw_peak_contact_force":0.7942,"tcp_end":[0.44417,-0.02546,0.11557],"tcp_start":[0.44694,-0.02561,0.02616],"tcp_to_object_dist_end":0.01768,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":677.0,"n_steps_budget":1000.0,"object_pos_end":[0.62526,0.19691,0.10522],"object_pos_start":[0.46162,-0.02541,0.1127],"object_to_goal_dist_end":0.01519,"object_to_goal_dist_start":0.28806,"object_z_max":0.11409,"peak_contact_force":0.11107,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21992.0,"raw_peak_contact_force":0.26032,"subtask_id":"reach_goal","tcp_end":[0.61759,0.19632,0.12102],"tcp_start":[0.44417,-0.02546,0.11557],"tcp_to_object_dist_end":0.01757,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.55556,"average_solve_count":81.0,"average_success_count":81.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.11547,"approach_object.speed":0.21613,"approach_object.tolerance":0.0354,"descend_grasp.descend_offset_z":0.01205,"descend_grasp.speed":0.27162,"lift.lift_height":0.14112,"lift.speed":0.21804,"lift.tolerance":0.02549,"place_at_goal.place_offset_z":0.01931,"place_at_goal.speed":0.21972,"place_at_goal.tolerance":0.02576},"optimized_scores":{"best_composite_score":0.33797,"best_fitness_score":0.97797,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":64.0,"contact_point_centroid":[0.54075,0.00073,-0.00143],"force_p95":0.75813,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.83806,"mean_force":0.25143,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52872,0.00085,0.02698]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3222.0,"contact_point_centroid":[0.5295,-0.01818,0.07672],"force_p95":0.11352,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39379,"mean_force":0.07414,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5269,0.0008,0.07426]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3488.0,"contact_point_centroid":[0.52947,0.01969,0.07399],"force_p95":0.1124,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37829,"mean_force":0.0698,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52692,0.0008,0.07198]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6824.0,"contact_point_centroid":[0.58872,0.09603,0.16792],"force_p95":0.11533,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2066,"mean_force":0.08005,"phase_index":4.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.58335,0.07759,0.16683]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5411.0,"contact_point_centroid":[0.58663,0.05623,0.16712],"force_p95":0.13821,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20561,"mean_force":0.09732,"phase_index":4.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.58139,0.07493,0.16579]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00099,-0.00203],"force_p95":0.13176,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15818,"mean_force":0.12532,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53161,0.0009,0.0274]},{"body_a":"world","body_b":"grasp_target","contact_count":708.0,"contact_point_centroid":[0.54431,0.00113,-0.00182],"force_p95":0.13761,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12332,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51551,0.00041,0.23837]},{"body_a":"world","body_b":"grasp_target","contact_count":3644.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53462,0.00093,0.09285]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53119,-0.01832,0.02866],"force_p95":0.07607,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11218,"mean_force":0.05173,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53035,0.00088,0.02595]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53116,0.01995,0.02778],"force_p95":0.06806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09597,"mean_force":0.04478,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53035,0.00088,0.02595]}],"total_contact_groups":10},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64741,0.148,0.17588],"final_tcp_position":[0.63707,0.14769,0.19712],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.83806,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":178.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":708.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53252,0.00085,0.17281],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14726,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":911.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3644.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53879,0.00103,0.03572],"tcp_start":[0.53252,0.00085,0.17281],"tcp_to_object_dist_end":0.01116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54416,0.00074,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25052,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12973,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15818,"tcp_end":[0.53032,0.00087,0.02591],"tcp_start":[0.53879,0.00103,0.03572],"tcp_to_object_dist_end":0.01384,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":218.0,"n_steps_budget":600.0,"object_pos_end":[0.54747,0.00085,0.1333],"object_pos_start":[0.54416,0.00074,0.02588],"object_to_goal_dist_end":0.19518,"object_to_goal_dist_start":0.25052,"object_z_max":0.13284,"peak_contact_force":0.10861,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6774.0,"raw_peak_contact_force":0.83806,"tcp_end":[0.52704,0.00081,0.13758],"tcp_start":[0.53032,0.00087,0.02591],"tcp_to_object_dist_end":0.02087,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":535.0,"n_steps_budget":1000.0,"object_pos_end":[0.64741,0.148,0.17588],"object_pos_start":[0.54747,0.00085,0.1333],"object_to_goal_dist_end":0.01826,"object_to_goal_dist_start":0.19518,"object_z_max":0.17583,"peak_contact_force":0.15874,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12235.0,"raw_peak_contact_force":0.2066,"subtask_id":"reach_goal","tcp_end":[0.63707,0.14769,0.19712],"tcp_start":[0.52704,0.00081,0.13758],"tcp_to_object_dist_end":0.02362,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```