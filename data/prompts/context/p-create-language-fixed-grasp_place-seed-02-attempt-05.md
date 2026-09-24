## Search State

- **Seed**: 2
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → approach → descend | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 9 | 0.3704 | 0.91 | ❌ rejected |
| 4 | approach → descend → grasp → approach → descend | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 9 | 0.4338 | 1.00 | ✅ accepted |
| 3 | approach → descend → grasp → approach → descend | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 9 | 0.3008 | 0.75 | ❌ rejected |
| 2 | approach → descend → grasp → approach → descend | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 9 | 0.4316 | 1.00 | ❌ rejected |
| 1 | approach → descend → grasp → approach → descend | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 9 | 0.4335 | 1.00 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.91). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.370) — your mutation base

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

- **Composite score**: 0.370
- **task_score** (E): 0.908
- **fitness_score**: 0.910  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 0.00 | 1.00 | 0.0979 |
| descend | 1.00 | 1.00 | 0.1454 |
| grasp | 1.00 | 1.00 | 0.0127 |
| transport | 1.00 | 1.00 | 0.2679 |
| place_descend | 1.00 | 1.00 | 0.0073 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.504, -0.006, 0.205) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.124 | 0.138 |
| descend | descend | 1.00 / step_budget | (0.504, -0.006, 0.205)→(0.491, -0.014, 0.061) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.124 |
| grasp | grasp | 1.00 / step_budget | (0.491, -0.014, 0.061)→(0.483, -0.013, 0.052) | (0.493, -0.015, 0.026)→(0.493, -0.014, 0.025) | 0.281→0.280 | 1.00 / 34.667 | 0.183 | 0.212 |
| transport | approach | 1.00 / step_budget | (0.483, -0.013, 0.052)→(0.618, 0.155, 0.205) | (0.493, -0.014, 0.025)→(0.625, 0.155, 0.169) | 0.280→0.027 | 1.00 / 16.667 | 0.140 | 0.399 |
| place_descend | descend | 1.00 / step_budget | (0.618, 0.155, 0.205)→(0.620, 0.158, 0.199) | (0.625, 0.155, 0.169)→(0.629, 0.158, 0.163) | 0.027→0.021 | 1.00 / 15.667 | 0.196 | 0.609 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.045
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.534
- phase_breakdown.transport_arc_score: 0.417
- phase_breakdown.approach_1_score: 0.040
- phase_breakdown.release_1_score: 0.479
- phase_breakdown.descend_1_score: 0.811
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.959

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.959
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.351
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: descend.grasp_z_offset
- **Final σ (mean)**: 0.488


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50612,"average_solve_count":245.0,"average_success_count":245.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.04146,"approach.speed":0.07362,"descend.grasp_z_offset":0.01,"descend.speed":0.09759,"place_descend.place_speed":0.02133,"place_descend.placement_z_offset":0.03307,"transport.arc_height":0.11791,"transport.placement_z_offset":0.02373,"transport.transport_speed":0.04362},"optimized_scores":{"best_composite_score":0.41873,"best_fitness_score":0.95873,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":196.0,"contact_point_centroid":[0.61724,0.1591,0.21669],"force_p95":0.28655,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.69186,"mean_force":0.15111,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61165,0.14067,0.21986]},{"body_a":"world","body_b":"grasp_target","contact_count":72.0,"contact_point_centroid":[0.47304,-0.01814,-0.00171],"force_p95":0.35439,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44002,"mean_force":0.13027,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.46698,-0.01816,0.05264]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":240.0,"contact_point_centroid":[0.61719,0.12287,0.21622],"force_p95":0.20263,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36965,"mean_force":0.12313,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61161,0.14062,0.21992]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6937.0,"contact_point_centroid":[0.50422,0.03905,0.17257],"force_p95":0.13357,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36113,"mean_force":0.09683,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50152,0.02057,0.17545]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7820.0,"contact_point_centroid":[0.49909,-0.00272,0.16414],"force_p95":0.13322,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36023,"mean_force":0.08905,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.49694,0.01566,0.16656]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47621,-0.02,-0.0022],"force_p95":0.17873,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23154,"mean_force":0.13694,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46963,-0.0178,0.05234]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3125.0,"contact_point_centroid":[0.47038,0.00131,0.04955],"force_p95":0.10582,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15735,"mean_force":0.06567,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46857,-0.01778,0.05126]},{"body_a":"world","body_b":"grasp_target","contact_count":268.0,"contact_point_centroid":[0.47616,-0.02015,-0.00153],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12469,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49933,-0.00325,0.26087]},{"body_a":"world","body_b":"grasp_target","contact_count":632.0,"contact_point_centroid":[0.47616,-0.02015,-0.002],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12295,"mean_force":0.12253,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.48376,-0.01384,0.11242]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4883.0,"contact_point_centroid":[0.46869,-0.03659,0.05124],"force_p95":0.08101,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08417,"mean_force":0.04506,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46858,-0.01778,0.05127]}],"total_contact_groups":10},"final_pose_error":0.02417,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62326,0.14315,0.18364],"final_tcp_position":[0.61405,0.14312,0.21816],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.69186,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":68.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.0259],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28845,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12308,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":268.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49737,-0.00925,0.18901],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16485,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":158.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.0259],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28845,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":632.0,"raw_peak_contact_force":0.12295,"subtask_id":"descend_1","tcp_end":[0.4768,-0.01789,0.06018],"tcp_start":[0.49737,-0.00925,0.18901],"tcp_to_object_dist_end":0.03424,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47612,-0.01838,0.02526],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28774,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.17482,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9808.0,"raw_peak_contact_force":0.23154,"subtask_id":"grasp_1","tcp_end":[0.46855,-0.01778,0.05123],"tcp_start":[0.4768,-0.01789,0.06018],"tcp_to_object_dist_end":0.02707,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":689.0,"n_steps_budget":1000.0,"object_pos_end":[0.61811,0.13893,0.18823],"object_pos_start":[0.47612,-0.01838,0.02526],"object_to_goal_dist_end":0.02431,"object_to_goal_dist_start":0.28774,"object_z_max":0.21301,"peak_contact_force":0.14645,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14829.0,"raw_peak_contact_force":0.44002,"subtask_id":"transport_arc","tcp_end":[0.61157,0.13905,0.22334],"tcp_start":[0.46855,-0.01778,0.05123],"tcp_to_object_dist_end":0.03571,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":28.0,"n_steps_budget":1000.0,"object_pos_end":[0.62326,0.14315,0.18364],"object_pos_start":[0.61811,0.13893,0.18823],"object_to_goal_dist_end":0.0191,"object_to_goal_dist_start":0.02431,"object_z_max":0.18823,"peak_contact_force":0.21971,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":436.0,"raw_peak_contact_force":0.69186,"subtask_id":"release_1","tcp_end":[0.61405,0.14312,0.21816],"tcp_start":[0.61157,0.13905,0.22334],"tcp_to_object_dist_end":0.03573,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42902,"average_solve_count":317.0,"average_success_count":317.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.08608,"approach.speed":0.06845,"descend.grasp_z_offset":0.01114,"descend.speed":0.02365,"place_descend.place_speed":0.09197,"place_descend.placement_z_offset":0.03963,"transport.arc_height":0.12629,"transport.placement_z_offset":0.04071,"transport.transport_speed":0.04267},"optimized_scores":{"best_composite_score":0.35113,"best_fitness_score":0.89113,"best_task_score":0.86856},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":162.0,"contact_point_centroid":[0.62022,0.2091,0.16333],"force_p95":0.35494,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.49062,"mean_force":0.14897,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61373,0.19066,0.16764]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":171.0,"contact_point_centroid":[0.6202,0.17261,0.16356],"force_p95":0.22196,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43282,"mean_force":0.13258,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61375,0.19068,0.1676]},{"body_a":"world","body_b":"grasp_target","contact_count":68.0,"contact_point_centroid":[0.45658,-0.02405,-0.0017],"force_p95":0.28731,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38123,"mean_force":0.09145,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.45084,-0.02351,0.05433]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7195.0,"contact_point_centroid":[0.50816,0.03051,0.16243],"force_p95":0.13619,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31987,"mean_force":0.09747,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.5053,0.04886,0.16585]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6983.0,"contact_point_centroid":[0.50901,0.06775,0.16519],"force_p95":0.13129,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31107,"mean_force":0.09856,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.5057,0.04938,0.1686]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4586,-0.02619,-0.00221],"force_p95":0.22805,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24098,"mean_force":0.16435,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45303,-0.02351,0.05393]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2644.0,"contact_point_centroid":[0.45255,-0.00465,0.05003],"force_p95":0.11114,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18501,"mean_force":0.08614,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.452,-0.02347,0.05293]},{"body_a":"world","body_b":"grasp_target","contact_count":224.0,"contact_point_centroid":[0.45856,-0.02632,-0.00142],"force_p95":0.13838,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12483,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49619,-0.00348,0.2743]},{"body_a":"world","body_b":"grasp_target","contact_count":988.0,"contact_point_centroid":[0.45856,-0.02632,-0.002],"force_p95":0.12284,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12508,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.47248,-0.01708,0.13564]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3393.0,"contact_point_centroid":[0.45251,-0.04238,0.05067],"force_p95":0.10089,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10992,"mean_force":0.07053,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45201,-0.02347,0.05294]}],"total_contact_groups":10},"final_pose_error":0.02428,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62455,0.19235,0.12693],"final_tcp_position":[0.61502,0.19233,0.16417],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.49062,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":57.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02586],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30369,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12536,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":224.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48953,-0.01034,0.22419],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20137,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":247.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02586],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30369,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":988.0,"raw_peak_contact_force":0.12508,"subtask_id":"descend_1","tcp_end":[0.45996,-0.02367,0.06124],"tcp_start":[0.48953,-0.01034,0.22419],"tcp_to_object_dist_end":0.03534,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45852,-0.02448,0.02526],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30248,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.21778,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7837.0,"raw_peak_contact_force":0.24098,"subtask_id":"grasp_1","tcp_end":[0.45198,-0.02347,0.0529],"tcp_start":[0.45996,-0.02367,0.06124],"tcp_to_object_dist_end":0.02842,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":713.0,"n_steps_budget":1000.0,"object_pos_end":[0.62131,0.1892,0.13477],"object_pos_start":[0.45852,-0.02448,0.02526],"object_to_goal_dist_end":0.02942,"object_to_goal_dist_start":0.30248,"object_z_max":0.18814,"peak_contact_force":0.13053,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14246.0,"raw_peak_contact_force":0.38123,"subtask_id":"transport_arc","tcp_end":[0.61407,0.1896,0.17166],"tcp_start":[0.45198,-0.02347,0.0529],"tcp_to_object_dist_end":0.0376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.62455,0.19235,0.12693],"object_pos_start":[0.62131,0.1892,0.13477],"object_to_goal_dist_end":0.02114,"object_to_goal_dist_start":0.02942,"object_z_max":0.13477,"peak_contact_force":0.15107,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":333.0,"raw_peak_contact_force":0.49062,"subtask_id":"release_1","tcp_end":[0.61502,0.19233,0.16417],"tcp_start":[0.61407,0.1896,0.17166],"tcp_to_object_dist_end":0.03845,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.80115,"average_solve_count":347.0,"average_success_count":347.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.08331,"approach.speed":0.04502,"descend.grasp_z_offset":0.01264,"descend.speed":0.02453,"place_descend.place_speed":0.0662,"place_descend.placement_z_offset":0.01368,"transport.arc_height":0.18952,"transport.placement_z_offset":0.02696,"transport.transport_speed":0.02068},"optimized_scores":{"best_composite_score":0.34145,"best_fitness_score":0.88145,"best_task_score":0.85452},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":150.0,"contact_point_centroid":[0.63497,0.15544,0.21288],"force_p95":0.27932,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.64387,"mean_force":0.15174,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.62927,0.137,0.2163]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6086.0,"contact_point_centroid":[0.55285,0.01465,0.15087],"force_p95":0.13352,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37456,"mean_force":0.0983,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54986,0.03291,0.15387]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6149.0,"contact_point_centroid":[0.5492,0.04672,0.14543],"force_p95":0.13709,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.363,"mean_force":0.09774,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54641,0.02845,0.14808]},{"body_a":"world","body_b":"grasp_target","contact_count":75.0,"contact_point_centroid":[0.54059,0.00021,-0.00174],"force_p95":0.32467,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3377,"mean_force":0.15229,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52666,0.00047,0.05194]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":173.0,"contact_point_centroid":[0.63482,0.11929,0.2125],"force_p95":0.2097,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31301,"mean_force":0.12029,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.62927,0.13698,0.21632]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54438,0.00114,-0.00209],"force_p95":0.14994,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16202,"mean_force":0.13003,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52919,0.00083,0.05221]},{"body_a":"world","body_b":"grasp_target","contact_count":344.0,"contact_point_centroid":[0.54431,0.00113,-0.00164],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12417,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50932,0.00023,0.2638]},{"body_a":"world","body_b":"grasp_target","contact_count":864.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12258,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.52883,0.00075,0.12557]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4379.0,"contact_point_centroid":[0.52949,-0.01814,0.05082],"force_p95":0.10374,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11112,"mean_force":0.05239,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52802,0.00081,0.05083]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4586.0,"contact_point_centroid":[0.52964,0.01964,0.05113],"force_p95":0.08801,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09947,"mean_force":0.04996,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52802,0.00081,0.05084]}],"total_contact_groups":10},"final_pose_error":0.02658,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.63964,0.13975,0.1786],"final_tcp_position":[0.63112,0.1392,0.21358],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.64387,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":87.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02599],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25014,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12209,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":344.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52597,0.0006,0.20082],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17579,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":216.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02599],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25014,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":864.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.53691,0.00096,0.06196],"tcp_start":[0.52597,0.0006,0.20082],"tcp_to_object_dist_end":0.0367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54448,0.00084,0.0253],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25071,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.15526,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10765.0,"raw_peak_contact_force":0.16202,"subtask_id":"grasp_1","tcp_end":[0.52799,0.00081,0.0508],"tcp_start":[0.53691,0.00096,0.06196],"tcp_to_object_dist_end":0.03036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":599.0,"n_steps_budget":1000.0,"object_pos_end":[0.63479,0.13541,0.1835],"object_pos_start":[0.54448,0.00084,0.0253],"object_to_goal_dist_end":0.02714,"object_to_goal_dist_start":0.25071,"object_z_max":0.19045,"peak_contact_force":0.14452,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12310.0,"raw_peak_contact_force":0.37456,"subtask_id":"transport_arc","tcp_end":[0.62881,0.1353,0.21868],"tcp_start":[0.52799,0.00081,0.0508],"tcp_to_object_dist_end":0.03568,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.63964,0.13975,0.1786],"object_pos_start":[0.63479,0.13541,0.1835],"object_to_goal_dist_end":0.02358,"object_to_goal_dist_start":0.02714,"object_z_max":0.1835,"peak_contact_force":0.21761,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":323.0,"raw_peak_contact_force":0.64387,"subtask_id":"release_1","tcp_end":[0.63112,0.1392,0.21358],"tcp_start":[0.62881,0.1353,0.21868],"tcp_to_object_dist_end":0.03601,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```