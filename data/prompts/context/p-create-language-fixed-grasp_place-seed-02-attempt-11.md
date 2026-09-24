## Search State

- **Seed**: 2
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | 0.1207 | 0.40 | ❌ rejected |
| 10 | approach → descend → grasp → approach → descend → release | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0919 | 0.39 | ❌ rejected |
| 9 | approach → descend → grasp → approach → descend | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 9 | 0.3153 | 0.77 | ❌ rejected |
| 8 | approach → descend → grasp → approach → descend | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 9 | 0.4332 | 1.00 | ❌ rejected |
| 7 | approach → descend → grasp → approach → descend | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 9 | 0.4051 | 0.95 | ❌ rejected |

**Proposal policy**: task_score is 0.40 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach_1 | object | (0.00, 0.00, 0.00) | distance | approach_height |
| descend_1 | object | (0.00, 0.00, 0.02) | distance | grasp_z_offset |
| grasp_1 | object | (0.00, 0.00, 0.02) | contact | — |
| transport_arc | goal | (0.00, 0.00, 0.00) | distance | — |
| release_1 | goal | (0.00, 0.00, 0.00) | distance | — |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.121) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
phases:
- id: approach
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
      - 0.03
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_1
- id: descend
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
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: descend_1
- id: grasp
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
  subtask_id: grasp_1
- id: transport
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    placement_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: place_descend
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
    - 0.03
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    placement_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **transport** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - placement_z_offset: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **place_descend** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - placement_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.121
- **task_score** (E): 0.398
- **fitness_score**: 0.671  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.550

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1771 |
| descend | 1.00 | 1.00 | 0.0811 |
| grasp | 1.00 | 1.00 | 0.0115 |
| transport | 0.00 | 1.00 | 0.2641 |
| place_descend | 1.00 | 1.00 | 0.0666 |
| release | 1.00 | 1.00 | 0.0202 |
| retract | 1.00 | 1.00 | 0.0667 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.490, -0.014, 0.128) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 7.600 | 0.138 |
| descend | descend | 1.00 / step_budget | (0.490, -0.014, 0.128)→(0.488, -0.015, 0.047) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.488, -0.015, 0.047)→(0.480, -0.015, 0.039) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 44.333 | 0.135 | 0.174 |
| transport | approach | 0.00 / step_budget | (0.480, -0.015, 0.039)→(0.602, 0.137, 0.211) | (0.493, -0.015, 0.026)→(0.608, 0.137, 0.190) | 0.281→0.054 | 1.00 / 36.333 | 0.081 | 0.474 |
| place_descend | descend | 1.00 / step_budget | (0.602, 0.137, 0.211)→(0.629, 0.170, 0.161) | (0.608, 0.137, 0.190)→(0.634, 0.170, 0.137) | 0.054→0.028 | 1.00 / 38.000 | 0.075 | 0.184 |
| release | release | 1.00 / step_budget | (0.629, 0.170, 0.161)→(0.623, 0.168, 0.180) | (0.634, 0.170, 0.137)→(0.619, 0.168, 0.025) | 0.028→0.142 | 1.00 / 2.667 | 0.238 | 1.458 |
| retract | retract | 1.00 / step_budget | (0.623, 0.168, 0.180)→(0.632, 0.173, 0.246) | (0.619, 0.168, 0.025)→(0.608, 0.166, 0.026) | 0.142→0.142 | 1.00 / 4.000 | 0.123 | 0.296 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.541
- phase_score: 0.475
- phase_breakdown.transport_arc_score: 0.193
- phase_breakdown.approach_1_score: 0.165
- phase_breakdown.release_1_score: 0.819
- phase_breakdown.descend_1_score: 0.883
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.743

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.743
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.541
- **Median Q (composite search score)**: 0.086
- **K-run variance**: 0.0026
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.349


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.68533,"average_solve_count":375.0,"average_success_count":375.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.09891,"approach.speed":0.03419,"descend.grasp_z_offset":0.01124,"descend.speed":0.01486,"place_descend.place_speed":0.0594,"release.release_duration":1.43332,"retract.retract_speed":0.06641,"transport.transport_speed":0.02963},"optimized_scores":{"best_composite_score":0.08634,"best_fitness_score":0.63634,"best_task_score":0.32749},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":168.0,"contact_point_centroid":[0.60911,0.14605,-0.00826],"force_p95":1.39214,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.66831,"mean_force":0.43725,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61902,0.15362,0.195]},{"body_a":"world","body_b":"grasp_target","contact_count":946.0,"contact_point_centroid":[0.60555,0.14267,-0.00245],"force_p95":0.34952,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44448,"mean_force":0.15104,"phase_index":6.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.62314,0.15586,0.24266]},{"body_a":"world","body_b":"grasp_target","contact_count":131.0,"contact_point_centroid":[0.47838,-0.0169,-0.00131],"force_p95":0.3454,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41058,"mean_force":0.24952,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.46437,-0.0177,0.03985]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1109.0,"contact_point_centroid":[0.62527,0.1739,0.18087],"force_p95":0.07822,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34004,"mean_force":0.05251,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62287,0.15479,0.18011]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1263.0,"contact_point_centroid":[0.62544,0.13569,0.18206],"force_p95":0.07448,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26926,"mean_force":0.04934,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62282,0.15478,0.18001]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18701.0,"contact_point_centroid":[0.52668,0.03105,0.13338],"force_p95":0.08084,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2285,"mean_force":0.05525,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52593,0.05013,0.13114]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18481.0,"contact_point_centroid":[0.53026,0.07295,0.13855],"force_p95":0.08107,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22183,"mean_force":0.05394,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52945,0.05387,0.13632]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7205.0,"contact_point_centroid":[0.61122,0.12056,0.20195],"force_p95":0.08568,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18962,"mean_force":0.05987,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.6094,0.13949,0.20048]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02006,-0.00204],"force_p95":0.136,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17627,"mean_force":0.12627,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46495,-0.01965,0.03934]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7371.0,"contact_point_centroid":[0.61099,0.15808,0.20195],"force_p95":0.08487,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15751,"mean_force":0.05842,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.60908,0.13917,0.20082]},{"body_a":"world","body_b":"grasp_target","contact_count":2124.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48643,-0.00892,0.21954]},{"body_a":"world","body_b":"grasp_target","contact_count":1396.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.47156,-0.01901,0.09235]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5075.0,"contact_point_centroid":[0.4636,-0.00037,0.04104],"force_p95":0.06595,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09728,"mean_force":0.04293,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46385,-0.01962,0.03824]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5393.0,"contact_point_centroid":[0.46348,-0.03887,0.04053],"force_p95":0.06486,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0846,"mean_force":0.04114,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46385,-0.01962,0.03825]}],"total_contact_groups":14},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.60248,0.14173,0.02602],"final_tcp_position":[0.6274,0.15772,0.27059],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.66831,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":532.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2124.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47439,-0.01835,0.13832],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11233,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":349.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1396.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47154,-0.0198,0.046],"tcp_start":[0.47439,-0.01835,0.13832],"tcp_to_object_dist_end":0.02051,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47606,-0.01971,0.02583],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28827,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13437,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12268.0,"raw_peak_contact_force":0.17627,"subtask_id":"grasp_1","tcp_end":[0.46382,-0.01962,0.03821],"tcp_start":[0.47154,-0.0198,0.046],"tcp_to_object_dist_end":0.01742,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59823,0.1194,0.20676],"object_pos_start":[0.47606,-0.01971,0.02583],"object_to_goal_dist_end":0.05446,"object_to_goal_dist_start":0.28827,"object_z_max":0.20658,"peak_contact_force":0.08231,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37313.0,"raw_peak_contact_force":0.41058,"subtask_id":"transport_arc","tcp_end":[0.59185,0.11957,0.22734],"tcp_start":[0.46382,-0.01962,0.03821],"tcp_to_object_dist_end":0.02155,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":418.0,"n_steps_budget":1000.0,"object_pos_end":[0.62906,0.15503,0.16112],"object_pos_start":[0.59823,0.1194,0.20676],"object_to_goal_dist_end":0.02929,"object_to_goal_dist_start":0.05446,"object_z_max":0.20688,"peak_contact_force":0.07512,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":14576.0,"raw_peak_contact_force":0.18962,"subtask_id":"release_1","tcp_end":[0.62458,0.15515,0.18397],"tcp_start":[0.59185,0.11957,0.22734],"tcp_to_object_dist_end":0.02328,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61831,0.15364,0.02333],"object_pos_start":[0.62906,0.15503,0.16112],"object_to_goal_dist_end":0.16729,"object_to_goal_dist_start":0.02929,"object_z_max":0.16112,"peak_contact_force":0.31931,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2540.0,"raw_peak_contact_force":1.66831,"tcp_end":[0.61898,0.15361,0.20349],"tcp_start":[0.62458,0.15515,0.18397],"tcp_to_object_dist_end":0.18016,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":299.0,"n_steps_budget":840.0,"object_pos_end":[0.60248,0.14173,0.02602],"object_pos_start":[0.61831,0.15364,0.02333],"object_to_goal_dist_end":0.16744,"object_to_goal_dist_start":0.16729,"object_z_max":0.02968,"peak_contact_force":0.12293,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":946.0,"raw_peak_contact_force":0.44448,"tcp_end":[0.6274,0.15772,0.27059],"tcp_start":[0.61898,0.15361,0.20349],"tcp_to_object_dist_end":0.24635,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.06061,"average_solve_count":297.0,"average_success_count":297.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.08027,"approach.speed":0.06496,"descend.grasp_z_offset":0.01062,"descend.speed":0.06123,"place_descend.place_speed":0.03214,"release.release_duration":0.91565,"retract.retract_speed":0.03645,"transport.transport_speed":0.04145},"optimized_scores":{"best_composite_score":0.19331,"best_fitness_score":0.74331,"best_task_score":0.54053},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":296.0,"contact_point_centroid":[0.60804,0.19932,-0.0039],"force_p95":0.79047,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.04254,"mean_force":0.24433,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61563,0.20072,0.11743]},{"body_a":"world","body_b":"grasp_target","contact_count":236.0,"contact_point_centroid":[0.46453,-0.01745,-0.00147],"force_p95":0.55397,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62462,"mean_force":0.35872,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.45009,-0.01903,0.04134]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1236.0,"contact_point_centroid":[0.6219,0.22178,0.10793],"force_p95":0.07012,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26936,"mean_force":0.0436,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62043,0.20249,0.10645]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21032.0,"contact_point_centroid":[0.52201,0.05553,0.10984],"force_p95":0.09111,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26143,"mean_force":0.0526,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.522,0.07462,0.10823]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17545.0,"contact_point_centroid":[0.52845,0.10128,0.11604],"force_p95":0.09411,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23292,"mean_force":0.0557,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52786,0.08204,0.11367]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1369.0,"contact_point_centroid":[0.62139,0.18336,0.1081],"force_p95":0.06322,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22493,"mean_force":0.0387,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62048,0.20251,0.10654]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02622,-0.00206],"force_p95":0.14189,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19274,"mean_force":0.12776,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44788,-0.02559,0.03931]},{"body_a":"world","body_b":"grasp_target","contact_count":1312.0,"contact_point_centroid":[0.60333,0.20229,-0.00198],"force_p95":0.13911,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17165,"mean_force":0.12277,"phase_index":6.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61917,0.20305,0.16141]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8181.0,"contact_point_centroid":[0.61009,0.20473,0.13957],"force_p95":0.07406,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15511,"mean_force":0.05045,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.60823,0.18564,0.13794]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7900.0,"contact_point_centroid":[0.61042,0.16724,0.13885],"force_p95":0.07526,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14629,"mean_force":0.052,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.60881,0.18636,0.13677]},{"body_a":"world","body_b":"grasp_target","contact_count":2304.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.13146,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.47829,-0.01183,0.21]},{"body_a":"world","body_b":"grasp_target","contact_count":1060.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.4549,-0.02493,0.08261]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4828.0,"contact_point_centroid":[0.44681,-0.00633,0.04061],"force_p95":0.06856,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10303,"mean_force":0.0449,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44681,-0.02555,0.03829]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5167.0,"contact_point_centroid":[0.44667,-0.04477,0.04011],"force_p95":0.06736,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07595,"mean_force":0.04292,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44682,-0.02555,0.03829]}],"total_contact_groups":14},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.60331,0.2023,0.02602],"final_tcp_position":[0.62503,0.20607,0.19502],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.04254,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":577.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2304.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45791,-0.02417,0.11995],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09396,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":265.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1060.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45427,-0.02581,0.0455],"tcp_start":[0.45791,-0.02417,0.11995],"tcp_to_object_dist_end":0.01995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45848,-0.0257,0.02576],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30329,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.1392,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11795.0,"raw_peak_contact_force":0.19274,"subtask_id":"grasp_1","tcp_end":[0.44679,-0.02555,0.03826],"tcp_start":[0.45427,-0.02581,0.0455],"tcp_to_object_dist_end":0.01711,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59977,0.16597,0.15433],"object_pos_start":[0.45848,-0.0257,0.02576],"object_to_goal_dist_end":0.06575,"object_to_goal_dist_start":0.30329,"object_z_max":0.15421,"peak_contact_force":0.07003,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38813.0,"raw_peak_contact_force":0.62462,"subtask_id":"transport_arc","tcp_end":[0.59456,0.16637,0.17537],"tcp_start":[0.44679,-0.02555,0.03826],"tcp_to_object_dist_end":0.02167,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":419.0,"n_steps_budget":1000.0,"object_pos_end":[0.62653,0.20277,0.08759],"object_pos_start":[0.59977,0.16597,0.15433],"object_to_goal_dist_end":0.02732,"object_to_goal_dist_start":0.06575,"object_z_max":0.1544,"peak_contact_force":0.07406,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16081.0,"raw_peak_contact_force":0.15511,"subtask_id":"release_1","tcp_end":[0.62248,0.20304,0.11031],"tcp_start":[0.59456,0.16637,0.17537],"tcp_to_object_dist_end":0.02308,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60286,0.20247,0.02637],"object_pos_start":[0.62653,0.20277,0.08759],"object_to_goal_dist_end":0.09206,"object_to_goal_dist_start":0.02732,"object_z_max":0.08759,"peak_contact_force":0.17146,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2901.0,"raw_peak_contact_force":1.04254,"tcp_end":[0.61549,0.20066,0.12949],"tcp_start":[0.62248,0.20304,0.11031],"tcp_to_object_dist_end":0.1039,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":328.0,"n_steps_budget":1000.0,"object_pos_end":[0.60331,0.2023,0.02602],"object_pos_start":[0.60286,0.20247,0.02637],"object_to_goal_dist_end":0.09228,"object_to_goal_dist_start":0.09206,"object_z_max":0.02637,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1312.0,"raw_peak_contact_force":0.17165,"tcp_end":[0.62503,0.20607,0.19502],"tcp_start":[0.61549,0.20066,0.12949],"tcp_to_object_dist_end":0.17043,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.94277,"average_solve_count":332.0,"average_success_count":332.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.08958,"approach.speed":0.02449,"descend.grasp_z_offset":0.01576,"descend.speed":0.08425,"place_descend.place_speed":0.07418,"release.release_duration":1.7265,"retract.retract_speed":0.02552,"transport.transport_speed":0.04299},"optimized_scores":{"best_composite_score":0.08246,"best_fitness_score":0.63246,"best_task_score":0.32699},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":123.0,"contact_point_centroid":[0.63621,0.15367,-0.01044],"force_p95":1.34796,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.6643,"mean_force":0.59838,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63457,0.15109,0.1972]},{"body_a":"world","body_b":"grasp_target","contact_count":130.0,"contact_point_centroid":[0.54484,0.00286,-0.00134],"force_p95":0.31987,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38541,"mean_force":0.2168,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52969,0.00247,0.04097]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1011.0,"contact_point_centroid":[0.64148,0.17136,0.1839],"force_p95":0.07918,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27941,"mean_force":0.053,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.6384,0.15226,0.18358]},{"body_a":"world","body_b":"grasp_target","contact_count":1065.0,"contact_point_centroid":[0.62359,0.15353,-0.00249],"force_p95":0.25376,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27266,"mean_force":0.15259,"phase_index":6.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.63897,0.15404,0.24291]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17488.0,"contact_point_centroid":[0.57353,0.0428,0.13303],"force_p95":0.08761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24773,"mean_force":0.05897,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.572,0.06184,0.13108]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1059.0,"contact_point_centroid":[0.64197,0.13325,0.18534],"force_p95":0.07429,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24289,"mean_force":0.04883,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63843,0.15227,0.18363]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17727.0,"contact_point_centroid":[0.57595,0.08388,0.1374],"force_p95":0.08281,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23574,"mean_force":0.05668,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.57431,0.0649,0.13589]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3917.0,"contact_point_centroid":[0.63363,0.12111,0.20674],"force_p95":0.08847,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20686,"mean_force":0.06174,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.63052,0.14004,0.20567]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3930.0,"contact_point_centroid":[0.63349,0.15846,0.20743],"force_p95":0.08854,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17585,"mean_force":0.06191,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.63017,0.13954,0.20649]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00103,-0.00203],"force_p95":0.13231,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15315,"mean_force":0.12546,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53108,0.00089,0.04107]},{"body_a":"world","body_b":"grasp_target","contact_count":2556.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13017,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51708,0.00048,0.21246]},{"body_a":"world","body_b":"grasp_target","contact_count":960.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.5364,0.00099,0.08766]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53087,-0.01833,0.04233],"force_p95":0.07626,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12223,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52986,0.00087,0.03964]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53081,0.01994,0.04145],"force_p95":0.06831,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09402,"mean_force":0.04469,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52986,0.00087,0.03964]}],"total_contact_groups":14},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.61865,0.15335,0.02602],"final_tcp_position":[0.64365,0.15648,0.2716],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":22.55497,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":640.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":22.55497,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2556.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53703,0.00099,0.1262],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":240.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":960.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53834,0.00103,0.04974],"tcp_start":[0.53703,0.00099,0.1262],"tcp_to_object_dist_end":0.02446,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5442,0.00077,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2505,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13057,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15315,"subtask_id":"grasp_1","tcp_end":[0.52982,0.00087,0.0396],"tcp_start":[0.53834,0.00103,0.04974],"tcp_to_object_dist_end":0.01988,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62742,0.12527,0.20888],"object_pos_start":[0.5442,0.00077,0.02587],"object_to_goal_dist_end":0.04244,"object_to_goal_dist_start":0.2505,"object_z_max":0.2087,"peak_contact_force":0.09129,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35345.0,"raw_peak_contact_force":0.38541,"subtask_id":"transport_arc","tcp_end":[0.62079,0.12561,0.2317],"tcp_start":[0.52982,0.00087,0.0396],"tcp_to_object_dist_end":0.02376,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":245.0,"n_steps_budget":1000.0,"object_pos_end":[0.64565,0.15234,0.1637],"object_pos_start":[0.62742,0.12527,0.20888],"object_to_goal_dist_end":0.02806,"object_to_goal_dist_start":0.04244,"object_z_max":0.20899,"peak_contact_force":0.07529,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7847.0,"raw_peak_contact_force":0.20686,"subtask_id":"release_1","tcp_end":[0.64013,0.15252,0.18763],"tcp_start":[0.62079,0.12561,0.2317],"tcp_to_object_dist_end":0.02455,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63626,0.14815,0.02539],"object_pos_start":[0.64565,0.15234,0.1637],"object_to_goal_dist_end":0.1664,"object_to_goal_dist_start":0.02806,"object_z_max":0.1637,"peak_contact_force":0.22464,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2193.0,"raw_peak_contact_force":1.6643,"tcp_end":[0.63453,0.15108,0.20643],"tcp_start":[0.64013,0.15252,0.18763],"tcp_to_object_dist_end":0.18107,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":339.0,"n_steps_budget":1000.0,"object_pos_end":[0.61865,0.15335,0.02602],"object_pos_start":[0.63626,0.14815,0.02539],"object_to_goal_dist_end":0.16767,"object_to_goal_dist_start":0.1664,"object_z_max":0.02993,"peak_contact_force":0.123,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1065.0,"raw_peak_contact_force":0.27266,"tcp_end":[0.64365,0.15648,0.2716],"tcp_start":[0.63453,0.15108,0.20643],"tcp_to_object_dist_end":0.24687,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```