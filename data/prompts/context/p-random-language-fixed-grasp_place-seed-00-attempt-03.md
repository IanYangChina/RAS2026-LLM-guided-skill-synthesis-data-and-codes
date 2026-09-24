## Search State

- **Seed**: 0
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.1187 | 0.21 | ✅ accepted |
| 2 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.1713 | 0.18 | ✅ accepted |
| 1 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.1716 | 0.18 | ❌ rejected |
| 0 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | -0.1716 | 0.18 | ✅ accepted |

**Proposal policy**: task_score is 0.21 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`
- Frozen object start: [0.5136961687321454, -0.02302132862361297, 0.03]
- Frozen task target: [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]
- Goal object position: (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5136961687321454, -0.02302132862361297, 0.03)
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
  frozen_object_start: [0.5137, -0.023, 0.03]
  frozen_task_target: [0.5541, 0.1517, 0.222]
  frozen_object_starts: {'grasp_target': [0.5136961687321454, -0.02302132862361297, 0.03]}
  frozen_targets: {'place_target': [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea

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

## Current Skill (Q=-0.119) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
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
    - 0.15
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_1
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
    - 0.02
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: descend_1
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
  subtask_id: grasp_1
- id: lift_1
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
    - 0.2
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
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: transport_arc
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
    - 0.1
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
    transport_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
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
  parameters:
    release_duration:
      type: scalar
      range:
      - 0.2
      - 2.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: release_1
- id: retract_1
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
    - -0.1
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
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15]
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02]
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.2]
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, -0.1]
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.119
- **task_score** (E): 0.208
- **fitness_score**: 0.581  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0990 |
| descend_1 | 1.00 | 1.00 | 0.1852 |
| grasp_1 | 1.00 | 1.00 | 0.0124 |
| lift_1 | 0.67 | 1.00 | 0.1423 |
| transport_arc | 0.00 | 1.00 | 0.0962 |
| release_1 | 1.00 | 1.00 | 0.0248 |
| retract_1 | 1.00 | 1.00 | 0.0908 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.001, 0.224) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.001, 0.224)→(0.492, 0.001, 0.039) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.492, 0.001, 0.039)→(0.483, 0.001, 0.030) | (0.497, 0.001, 0.026)→(0.497, 0.000, 0.026) | 0.265→0.266 | 1.00 / 42.667 | 0.144 | 0.186 |
| lift_1 | lift | 0.67 / step_budget | (0.483, 0.001, 0.030)→(0.480, 0.000, 0.172) | (0.497, 0.000, 0.026)→(0.490, 0.000, 0.159) | 0.266→0.215 | 1.00 / 37.000 | 0.082 | 0.665 |
| transport_arc | approach | 0.00 / step_budget | (0.480, 0.000, 0.172)→(0.502, 0.045, 0.253) | (0.490, 0.000, 0.159)→(0.509, 0.045, 0.234) | 0.215→0.170 | 1.00 / 32.667 | 0.089 | 0.125 |
| release_1 | release | 1.00 / step_budget | (0.502, 0.045, 0.253)→(0.498, 0.044, 0.277) | (0.509, 0.045, 0.234)→(0.506, 0.044, 0.000) | 0.170→0.250 | 1.00 / 4.000 | 0.326 | 1.993 |
| retract_1 | retract | 1.00 / step_budget | (0.498, 0.044, 0.277)→(0.494, 0.044, 0.186) | (0.506, 0.044, 0.000)→(0.507, 0.045, 0.016) | 0.250→0.237 | 1.00 / 4.000 | 0.123 | 0.305 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.246
- phase_score: 0.243
- phase_breakdown.release_1_score: 0.016
- phase_breakdown.approach_1_score: 0.003
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.021
- phase_breakdown.descend_1_score: 0.786
- grasp_place_fitness: 0.601

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.601
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.246
- **Median Q (composite search score)**: -0.128
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.399


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `096c354712624ed6bd8f9b9cbbbc2b7d35a94d9c1517cfb8353e2e383be5aaf0`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3798aa6551d21849355469c7d63897f628ac7de9267c18bb4301fe6cfaae0164`; realized-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5137,-0.02302,0.03]},{"name":"goal","value":[0.5541,0.15165,0.22199]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5137,-0.02302,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5541,0.15165,0.22199]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.76836,"average_solve_count":354.0,"average_success_count":354.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.0569,"approach_1.approach_speed":0.0197,"descend_1.descend_speed":0.02924,"descend_1.grasp_z_offset":0.00433,"lift_1.lift_height":0.18367,"lift_1.lift_speed":0.0908,"release_1.release_duration":1.11835,"retract_1.retract_speed":0.01529,"transport_arc.arc_height":0.05069,"transport_arc.transport_height":0.09165,"transport_arc.transport_speed":0.06492},"optimized_scores":{"best_composite_score":-0.12819,"best_fitness_score":0.57181,"best_task_score":0.19066},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":120.0,"contact_point_centroid":[0.51181,0.01802,-0.01007],"force_p95":1.6453,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.76832,"mean_force":0.677,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50204,0.01813,0.28203]},{"body_a":"world","body_b":"grasp_target","contact_count":151.0,"contact_point_centroid":[0.51015,-0.02228,-0.00113],"force_p95":0.47788,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6982,"mean_force":0.1116,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49743,-0.02242,0.03045]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.49552,-0.04155,0.10326],"force_p95":0.08082,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3368,"mean_force":0.05894,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49484,-0.02236,0.10058]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20494.0,"contact_point_centroid":[0.49659,-0.00341,0.10086],"force_p95":0.07596,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33008,"mean_force":0.05049,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49485,-0.02236,0.09924]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5137,-0.02307,-0.00205],"force_p95":0.13891,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1755,"mean_force":0.12656,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50032,-0.02248,0.0301]},{"body_a":"world","body_b":"grasp_target","contact_count":2800.0,"contact_point_centroid":[0.5137,-0.02302,-0.00195],"force_p95":0.12893,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50296,-0.01055,0.19725]},{"body_a":"world","body_b":"grasp_target","contact_count":1268.0,"contact_point_centroid":[0.51467,0.01818,-0.00221],"force_p95":0.12463,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1363,"mean_force":0.11616,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49954,0.01803,0.24291]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16364.0,"contact_point_centroid":[0.49892,-0.02579,0.2214],"force_p95":0.08701,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12288,"mean_force":0.05942,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49733,-0.00678,0.21971]},{"body_a":"world","body_b":"grasp_target","contact_count":808.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50678,-0.02199,0.06652]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17336.0,"contact_point_centroid":[0.49922,0.01166,0.21966],"force_p95":0.08139,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10776,"mean_force":0.05624,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49719,-0.00724,0.21867]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5306.0,"contact_point_centroid":[0.50021,-0.0034,0.03081],"force_p95":0.06762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10708,"mean_force":0.0412,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49907,-0.02245,0.02876]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":966.0,"contact_point_centroid":[0.50675,0.03734,0.26153],"force_p95":0.08012,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09972,"mean_force":0.05303,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50488,0.01832,0.26032]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4170.0,"contact_point_centroid":[0.49867,-0.04173,0.0318],"force_p95":0.07977,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09193,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49908,-0.02245,0.02876]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":994.0,"contact_point_centroid":[0.50808,-0.00062,0.26154],"force_p95":0.08326,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08482,"mean_force":0.05066,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5048,0.01831,0.26018]}],"total_contact_groups":14},"final_pose_error":0.00987,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.51466,0.01818,0.01602],"final_tcp_position":[0.49857,0.01798,0.1962],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":1.76832,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":701.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2800.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50839,-0.02145,0.09498],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06918,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":202.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":808.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50772,-0.02261,0.03814],"tcp_start":[0.50839,-0.02145,0.09498],"tcp_to_object_dist_end":0.01352,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51357,-0.02287,0.02582],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26568,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.13883,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11276.0,"raw_peak_contact_force":0.1755,"subtask_id":"grasp_1","tcp_end":[0.49904,-0.02245,0.02872],"tcp_start":[0.50772,-0.02261,0.03814],"tcp_to_object_dist_end":0.01482,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50583,-0.02299,0.16342],"object_pos_start":[0.51357,-0.02287,0.02582],"object_to_goal_dist_end":0.19043,"object_to_goal_dist_start":0.26568,"object_z_max":0.16325,"peak_contact_force":0.08286,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37645.0,"raw_peak_contact_force":0.6982,"tcp_end":[0.49524,-0.02236,0.17506],"tcp_start":[0.49904,-0.02245,0.02872],"tcp_to_object_dist_end":0.01575,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51303,0.01849,0.2447],"object_pos_start":[0.50583,-0.02299,0.16342],"object_to_goal_dist_end":0.14119,"object_to_goal_dist_start":0.19043,"object_z_max":0.24465,"peak_contact_force":0.09178,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33700.0,"raw_peak_contact_force":0.12288,"subtask_id":"transport_arc","tcp_end":[0.50605,0.01826,0.26255],"tcp_start":[0.49524,-0.02236,0.17506],"tcp_to_object_dist_end":0.01916,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51313,0.0182,0.00291],"object_pos_start":[0.51303,0.01849,0.2447],"object_to_goal_dist_end":0.25977,"object_to_goal_dist_start":0.14119,"object_z_max":0.24471,"peak_contact_force":0.148,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2080.0,"raw_peak_contact_force":1.76832,"subtask_id":"release_1","tcp_end":[0.502,0.01813,0.28695],"tcp_start":[0.50605,0.01826,0.26255],"tcp_to_object_dist_end":0.28425,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":317.0,"n_steps_budget":1000.0,"object_pos_end":[0.51466,0.01818,0.01602],"object_pos_start":[0.51313,0.0182,0.00291],"object_to_goal_dist_end":0.24859,"object_to_goal_dist_start":0.25977,"object_z_max":0.01673,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1268.0,"raw_peak_contact_force":0.1363,"tcp_end":[0.49857,0.01798,0.1962],"tcp_start":[0.502,0.01813,0.28695],"tcp_to_object_dist_end":0.1809,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `ed2df336ade3d991e9495251c8398520a59dd014a70bd2d7bb71dc7aefccaa8a`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.19262,"average_solve_count":244.0,"average_success_count":244.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.29412,"approach_1.approach_speed":0.07376,"descend_1.descend_speed":0.0271,"descend_1.grasp_z_offset":0.00449,"lift_1.lift_height":0.1305,"lift_1.lift_speed":0.07385,"release_1.release_duration":0.44914,"retract_1.retract_speed":0.04705,"transport_arc.arc_height":0.06561,"transport_arc.transport_height":0.1202,"transport_arc.transport_speed":0.09433},"optimized_scores":{"best_composite_score":-0.09939,"best_fitness_score":0.60061,"best_task_score":0.24642},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.50013,0.09189,-0.01396],"force_p95":2.12991,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.14511,"mean_force":0.89762,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49555,0.09005,0.26219]},{"body_a":"world","body_b":"grasp_target","contact_count":165.0,"contact_point_centroid":[0.49631,0.04249,-0.00126],"force_p95":0.43458,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65765,"mean_force":0.11261,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48591,0.04343,0.03161]},{"body_a":"world","body_b":"grasp_target","contact_count":1172.0,"contact_point_centroid":[0.49702,0.094,-0.00232],"force_p95":0.14032,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52945,"mean_force":0.12006,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49293,0.08963,0.2213]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.4834,0.0624,0.0918],"force_p95":0.08404,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3327,"mean_force":0.05853,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48337,0.04321,0.08905]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20803.0,"contact_point_centroid":[0.48532,0.02429,0.08971],"force_p95":0.07839,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30827,"mean_force":0.0493,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48337,0.04321,0.08818]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50125,0.04498,-0.00212],"force_p95":0.15877,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21525,"mean_force":0.13208,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4889,0.04371,0.03123]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5018.0,"contact_point_centroid":[0.48945,0.0246,0.03129],"force_p95":0.0757,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17775,"mean_force":0.04312,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48767,0.0436,0.02993]},{"body_a":"world","body_b":"grasp_target","contact_count":1404.0,"contact_point_centroid":[0.50118,0.04505,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49831,0.02133,0.30695]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16554.0,"contact_point_centroid":[0.48733,0.08056,0.20083],"force_p95":0.08796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12929,"mean_force":0.05878,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.4878,0.06143,0.19841]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1184.0,"contact_point_centroid":[0.5033,0.07221,0.24017],"force_p95":0.08185,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12337,"mean_force":0.04803,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49845,0.09067,0.23994]},{"body_a":"world","body_b":"grasp_target","contact_count":3680.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4964,0.04214,0.17615]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19283.0,"contact_point_centroid":[0.49111,0.04256,0.19905],"force_p95":0.0767,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11522,"mean_force":0.05123,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48772,0.06122,0.19806]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":891.0,"contact_point_centroid":[0.49785,0.10977,0.24198],"force_p95":0.08836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10585,"mean_force":0.05535,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49857,0.0907,0.24013]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4222.0,"contact_point_centroid":[0.48774,0.06291,0.03256],"force_p95":0.08592,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09411,"mean_force":0.05194,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48767,0.0436,0.02994]}],"total_contact_groups":14},"final_pose_error":0.00976,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.49717,0.09478,0.01602],"final_tcp_position":[0.49195,0.08945,0.17587],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":2.14511,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":352.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1404.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49864,0.04007,0.31584],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.28988,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":920.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3680.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.4962,0.04437,0.03903],"tcp_start":[0.49864,0.04007,0.31584],"tcp_to_object_dist_end":0.01395,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50116,0.04416,0.02557],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24284,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15654,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11040.0,"raw_peak_contact_force":0.21525,"subtask_id":"grasp_1","tcp_end":[0.48764,0.04359,0.0299],"tcp_start":[0.4962,0.04437,0.03903],"tcp_to_object_dist_end":0.01421,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49337,0.04413,0.13725],"object_pos_start":[0.50116,0.04416,0.02557],"object_to_goal_dist_end":0.21315,"object_to_goal_dist_start":0.24284,"object_z_max":0.13715,"peak_contact_force":0.07957,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37968.0,"raw_peak_contact_force":0.65765,"tcp_end":[0.48368,0.04324,0.14947],"tcp_start":[0.48764,0.04359,0.0299],"tcp_to_object_dist_end":0.01562,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50671,0.09231,0.22431],"object_pos_start":[0.49337,0.04413,0.13725],"object_to_goal_dist_end":0.1806,"object_to_goal_dist_start":0.21315,"object_z_max":0.22423,"peak_contact_force":0.08805,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35837.0,"raw_peak_contact_force":0.12929,"subtask_id":"transport_arc","tcp_end":[0.49981,0.09074,0.24233],"tcp_start":[0.48368,0.04324,0.14947],"tcp_to_object_dist_end":0.01936,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49817,0.08666,-0.00381],"object_pos_start":[0.50671,0.09231,0.22431],"object_to_goal_dist_end":0.22824,"object_to_goal_dist_start":0.1806,"object_z_max":0.22432,"peak_contact_force":0.55892,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2167.0,"raw_peak_contact_force":2.14511,"subtask_id":"release_1","tcp_end":[0.49551,0.09005,0.26681],"tcp_start":[0.49981,0.09074,0.24233],"tcp_to_object_dist_end":0.27065,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":300.0,"n_steps_budget":1000.0,"object_pos_end":[0.49717,0.09478,0.01602],"object_pos_start":[0.49817,0.08666,-0.00381],"object_to_goal_dist_end":0.21011,"object_to_goal_dist_start":0.22824,"object_z_max":0.01759,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1172.0,"raw_peak_contact_force":0.52945,"tcp_end":[0.49195,0.08945,0.17587],"tcp_start":[0.49551,0.09005,0.26681],"tcp_to_object_dist_end":0.16002,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `291bc6f2bd023fc25503740a7343328e565e43fc71fa3c9c5d2fdbe2d4351fd2`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25366,"average_solve_count":205.0,"average_success_count":205.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.22371,"approach_1.approach_speed":0.06981,"descend_1.descend_speed":0.05922,"descend_1.grasp_z_offset":0.00434,"lift_1.lift_height":0.21502,"lift_1.lift_speed":0.09934,"release_1.release_duration":1.4259,"retract_1.retract_speed":0.07571,"transport_arc.arc_height":0.05628,"transport_arc.transport_height":0.06919,"transport_arc.transport_speed":0.01186},"optimized_scores":{"best_composite_score":-0.12855,"best_fitness_score":0.57145,"best_task_score":0.18663},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":105.0,"contact_point_centroid":[0.50485,0.02187,-0.01052],"force_p95":1.67693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06624,"mean_force":0.77786,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49553,0.0249,0.2731]},{"body_a":"world","body_b":"grasp_target","contact_count":131.0,"contact_point_centroid":[0.47271,-0.01922,-0.0011],"force_p95":0.40181,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63945,"mean_force":0.09138,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46182,-0.01959,0.03268]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20780.0,"contact_point_centroid":[0.46078,-0.00054,0.11068],"force_p95":0.0734,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31762,"mean_force":0.04953,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45929,-0.01954,0.10898]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17783.0,"contact_point_centroid":[0.45961,-0.03873,0.11159],"force_p95":0.07971,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31642,"mean_force":0.05636,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45929,-0.01954,0.10891]},{"body_a":"world","body_b":"grasp_target","contact_count":1132.0,"contact_point_centroid":[0.51023,0.02341,-0.00227],"force_p95":0.12687,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24803,"mean_force":0.11705,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49308,0.02477,0.23335]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1104.0,"contact_point_centroid":[0.501,0.00615,0.25189],"force_p95":0.08783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17633,"mean_force":0.05317,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49832,0.02511,0.25073]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1113.0,"contact_point_centroid":[0.49938,0.04408,0.25202],"force_p95":0.08512,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17091,"mean_force":0.05172,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49839,0.02511,0.25085]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02018,-0.00204],"force_p95":0.13763,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16655,"mean_force":0.12609,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46449,-0.01964,0.03205]},{"body_a":"world","body_b":"grasp_target","contact_count":596.0,"contact_point_centroid":[0.47616,-0.02015,-0.00179],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12345,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49004,-0.00675,0.28124]},{"body_a":"world","body_b":"grasp_target","contact_count":2988.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47449,-0.01724,0.14894]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17469.0,"contact_point_centroid":[0.47818,-0.0178,0.22597],"force_p95":0.08555,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12192,"mean_force":0.0559,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.47659,0.00124,0.22408]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5071.0,"contact_point_centroid":[0.46445,-0.00053,0.0324],"force_p95":0.06808,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10808,"mean_force":0.04308,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46329,-0.01962,0.03087]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18114.0,"contact_point_centroid":[0.47832,0.02045,0.22581],"force_p95":0.07936,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10731,"mean_force":0.05385,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.4768,0.00145,0.22436]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4408.0,"contact_point_centroid":[0.46286,-0.03887,0.03361],"force_p95":0.07739,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09248,"mean_force":0.04914,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46329,-0.01962,0.03087]}],"total_contact_groups":14},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.51019,0.02344,0.01602],"final_tcp_position":[0.49202,0.02471,0.18709],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":2.06624,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":150.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":596.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47976,-0.01479,0.26096],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23503,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":747.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2988.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.47162,-0.01975,0.03917],"tcp_start":[0.47976,-0.01479,0.26096],"tcp_to_object_dist_end":0.01392,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47604,-0.01997,0.02584],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28843,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.1376,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11279.0,"raw_peak_contact_force":0.16655,"subtask_id":"grasp_1","tcp_end":[0.46326,-0.01962,0.03084],"tcp_start":[0.47162,-0.01975,0.03917],"tcp_to_object_dist_end":0.01373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46936,-0.02012,0.17776],"object_pos_start":[0.47604,-0.01997,0.02584],"object_to_goal_dist_end":0.24201,"object_to_goal_dist_start":0.28843,"object_z_max":0.17757,"peak_contact_force":0.08307,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38694.0,"raw_peak_contact_force":0.63945,"tcp_end":[0.4597,-0.01953,0.19158],"tcp_start":[0.46326,-0.01962,0.03084],"tcp_to_object_dist_end":0.01687,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50638,0.02538,0.23381],"object_pos_start":[0.46936,-0.02012,0.17776],"object_to_goal_dist_end":0.18831,"object_to_goal_dist_start":0.24201,"object_z_max":0.23378,"peak_contact_force":0.08688,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35583.0,"raw_peak_contact_force":0.12192,"subtask_id":"transport_arc","tcp_end":[0.49968,0.0251,0.2532],"tcp_start":[0.4597,-0.01953,0.19158],"tcp_to_object_dist_end":0.02051,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50759,0.0257,0.00212],"object_pos_start":[0.50638,0.02538,0.23381],"object_to_goal_dist_end":0.26164,"object_to_goal_dist_start":0.18831,"object_z_max":0.23381,"peak_contact_force":0.27112,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2322.0,"raw_peak_contact_force":2.06624,"subtask_id":"release_1","tcp_end":[0.49549,0.0249,0.27776],"tcp_start":[0.49968,0.0251,0.2532],"tcp_to_object_dist_end":0.2759,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":283.0,"n_steps_budget":840.0,"object_pos_end":[0.51019,0.02344,0.01602],"object_pos_start":[0.50759,0.0257,0.00212],"object_to_goal_dist_end":0.25179,"object_to_goal_dist_start":0.26164,"object_z_max":0.01674,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1132.0,"raw_peak_contact_force":0.24803,"tcp_end":[0.49202,0.02471,0.18709],"tcp_start":[0.49549,0.0249,0.27776],"tcp_to_object_dist_end":0.17204,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```